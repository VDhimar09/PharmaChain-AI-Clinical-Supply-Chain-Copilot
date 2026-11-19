import time
from dataclasses import dataclass
from typing import Literal

from fastapi import Request
from prometheus_client import Counter, Histogram

HTTP_REQUESTS_TOTAL = Counter(
    "pharmachain_http_requests_total",
    "Total number of HTTP requests handled by the PharmaChain API.",
    ["method", "route", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "pharmachain_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["method", "route"],
)

HTTP_ERRORS_TOTAL = Counter(
    "pharmachain_http_errors_total",
    "Total number of HTTP 4xx and 5xx responses.",
    ["method", "route", "status"],
)


AI_REQUESTS_TOTAL = Counter(
    "pharmachain_ai_requests_total",
    "Total number of OpenAI API requests attempted by PharmaChain.",
    ["provider", "operation", "model", "outcome"],
)

AI_REQUEST_DURATION_SECONDS = Histogram(
    "pharmachain_ai_request_duration_seconds",
    "Duration of OpenAI API requests in seconds.",
    ["provider", "operation", "model", "outcome"],
)

AI_TOKENS_TOTAL = Counter(
    "pharmachain_ai_tokens_total",
    "OpenAI tokens reported by successful API responses.",
    ["provider", "operation", "model", "token_type"],
)

AI_COST_USD_TOTAL = Counter(
    "pharmachain_ai_cost_usd_total",
    "Estimated USD cost for OpenAI requests with verified model pricing.",
    ["provider", "operation", "model"],
)


@dataclass(frozen=True)
class OpenAIModelPricing:
    """Verified OpenAI prices in USD per million tokens.

    ``output_usd_per_million_tokens`` is omitted for embedding-only models.
    Pricing is intentionally empty until verified rates are supplied by the
    deployment or finance owner.
    """

    input_usd_per_million_tokens: float
    output_usd_per_million_tokens: float | None = None


# Do not populate this registry with unverified prices. A deployment may call
# ``configure_openai_model_pricing`` with verified canonical model rates.
OPENAI_MODEL_PRICING: dict[str, OpenAIModelPricing] = {}


def configure_openai_model_pricing(
    pricing: dict[str, OpenAIModelPricing],
) -> None:
    """Replace the verified model-pricing registry used for cost estimates."""

    for model, rates in pricing.items():
        if not model.strip() or rates.input_usd_per_million_tokens < 0:
            raise ValueError("OpenAI model pricing must use non-negative rates.")
        if (
            rates.output_usd_per_million_tokens is not None
            and rates.output_usd_per_million_tokens < 0
        ):
            raise ValueError("OpenAI model pricing must use non-negative rates.")

    OPENAI_MODEL_PRICING.clear()
    OPENAI_MODEL_PRICING.update(pricing)


def record_openai_usage(
    *,
    operation: Literal["embeddings", "chat_completions"],
    model: str,
    outcome: Literal["success", "error", "invalid_response"],
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    duration_seconds: float | None = None,
) -> None:
    """Record safe, low-cardinality OpenAI request metrics.

    Instrumentation is deliberately best-effort: no metrics failure may alter
    an AI request. Token and cost counters are omitted when response usage or
    verified pricing is unavailable.
    """

    try:
        if operation not in {"embeddings", "chat_completions"}:
            return
        if outcome not in {"success", "error", "invalid_response"}:
            return

        canonical_model = model.strip()
        if not canonical_model:
            return

        labels = {
            "provider": "openai",
            "operation": operation,
            "model": canonical_model,
        }
        AI_REQUESTS_TOTAL.labels(**labels, outcome=outcome).inc()

        if duration_seconds is not None and duration_seconds >= 0:
            AI_REQUEST_DURATION_SECONDS.labels(**labels, outcome=outcome).observe(
                duration_seconds
            )

        valid_input_tokens = _non_negative_token_count(input_tokens)
        valid_output_tokens = _non_negative_token_count(output_tokens)

        if valid_input_tokens is not None:
            AI_TOKENS_TOTAL.labels(**labels, token_type="input").inc(
                valid_input_tokens
            )
        if valid_output_tokens is not None:
            AI_TOKENS_TOTAL.labels(**labels, token_type="output").inc(
                valid_output_tokens
            )

        estimated_cost = _estimate_openai_cost(
            operation=operation,
            model=canonical_model,
            input_tokens=valid_input_tokens,
            output_tokens=valid_output_tokens,
        )
        if estimated_cost is not None:
            AI_COST_USD_TOTAL.labels(**labels).inc(estimated_cost)
    except Exception:
        # Metrics must never disrupt a provider call or expose its contents.
        return


def _non_negative_token_count(value: int | None) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _estimate_openai_cost(
    *,
    operation: str,
    model: str,
    input_tokens: int | None,
    output_tokens: int | None,
) -> float | None:
    pricing = OPENAI_MODEL_PRICING.get(model)
    if pricing is None or input_tokens is None:
        return None

    input_cost = input_tokens * pricing.input_usd_per_million_tokens / 1_000_000
    if operation == "embeddings":
        return input_cost

    if output_tokens is None or pricing.output_usd_per_million_tokens is None:
        return None

    return input_cost + (
        output_tokens * pricing.output_usd_per_million_tokens / 1_000_000
    )


async def metrics_middleware(request: Request, call_next):
    """Record safe, low-cardinality HTTP metrics."""

    if request.url.path == "/metrics":
        return await call_next(request)

    start = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start

    route = request.scope.get("route")
    route_path = getattr(route, "path", request.url.path)

    method = request.method
    status = str(response.status_code)

    HTTP_REQUESTS_TOTAL.labels(
        method=method,
        route=route_path,
        status=status,
    ).inc()

    HTTP_REQUEST_DURATION_SECONDS.labels(
        method=method,
        route=route_path,
    ).observe(duration)

    if response.status_code >= 400:
        HTTP_ERRORS_TOTAL.labels(
            method=method,
            route=route_path,
            status=status,
        ).inc()

    return response
