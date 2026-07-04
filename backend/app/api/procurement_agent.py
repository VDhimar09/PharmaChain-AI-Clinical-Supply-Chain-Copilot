from dataclasses import dataclass


@dataclass
class ProcurementDecision:

    decision: str

    confidence: float

    reasoning: list

    projected_occupancy: float


class ProcurementAgent:

    MAX_OCCUPANCY = 90

    def evaluate(
        self,
        current_occupancy: float,
        projected_occupancy: float,
        temperature_match: bool,
        incoming_conflict: bool
    ):

        reasoning = []

        if not temperature_match:

            reasoning.append(
                "Temperature requirements do not match storage zone."
            )

            return ProcurementDecision(
                decision="REJECT",
                confidence=0.98,
                reasoning=reasoning,
                projected_occupancy=projected_occupancy
            )

        if projected_occupancy > self.MAX_OCCUPANCY:

            reasoning.append(
                f"Projected occupancy exceeds {self.MAX_OCCUPANCY}%."
            )

            return ProcurementDecision(
                decision="REJECT",
                confidence=0.95,
                reasoning=reasoning,
                projected_occupancy=projected_occupancy
            )

        if incoming_conflict:

            reasoning.append(
                "Incoming shipments may impact available capacity."
            )

            return ProcurementDecision(
                decision="REVIEW",
                confidence=0.75,
                reasoning=reasoning,
                projected_occupancy=projected_occupancy
            )

        reasoning.append(
            "Capacity available."
        )

        reasoning.append(
            "Temperature requirements satisfied."
        )

        return ProcurementDecision(
            decision="APPROVE",
            confidence=0.92,
            reasoning=reasoning,
            projected_occupancy=projected_occupancy
        )