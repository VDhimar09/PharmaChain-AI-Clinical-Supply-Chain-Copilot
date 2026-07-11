import { ApiError, ApiErrorBody, ApiQueryParams } from "./types";
import {
  clearStoredAuthSession,
  getStoredAuthSession,
  setStoredAuthSession,
} from "@/lib/auth/token-storage";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export function getApiBaseUrl(): string {
  const fallbackOrigin = typeof window !== "undefined" ? window.location.origin : "http://localhost:5173";
  return API_BASE_URL || fallbackOrigin;
}

export interface ApiRequestOptions extends Omit<RequestInit, "body" | "headers"> {
  query?: ApiQueryParams;
  data?: unknown;
  headers?: HeadersInit;
  skipAuthHeader?: boolean;
  skipAuthRefresh?: boolean;
}

export class ApiClient {
  constructor(public baseUrl = getApiBaseUrl()) {}

  private buildUrl(path: string, query?: ApiQueryParams): string {
    const rawPath = path.startsWith("/") ? path : `/${path}`;
    const base = this.baseUrl || (typeof window !== "undefined" ? window.location.origin : "http://localhost:5173");
    const url = new URL(rawPath, base);

    if (query) {
      Object.entries(query).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.set(key, String(value));
        }
      });
    }

    return url.toString();
  }

  private buildHeaders(customHeaders?: HeadersInit, skipAuthHeader = false): Headers {
    const headers = new Headers(customHeaders);
    const session = getStoredAuthSession();

    if (!headers.has("Accept")) {
      headers.set("Accept", "application/json");
    }

    if (!headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }

    if (!skipAuthHeader && session?.accessToken && !headers.has("Authorization")) {
      headers.set("Authorization", `Bearer ${session.accessToken}`);
    }

    return headers;
  }

  private async parseResponse<T>(response: Response): Promise<T> {
    const text = await response.text();
    const contentType = response.headers.get("content-type") ?? "";

    let body: unknown = text;
    if (text && contentType.includes("application/json")) {
      try {
        body = JSON.parse(text);
      } catch {
        body = text;
      }
    }

    if (!response.ok) {
      const payload = typeof body === "object" && body !== null ? (body as ApiErrorBody) : null;
      throw new ApiError(response.status, response.statusText, payload);
    }

    return body as T;
  }

  async request<T = unknown>(path: string, options: ApiRequestOptions = {}): Promise<T> {
    const {
      query,
      data,
      headers,
      skipAuthHeader,
      skipAuthRefresh,
      ...fetchOptions
    } = options;
    const url = this.buildUrl(path, query);

    const init: RequestInit = {
      ...fetchOptions,
      method: fetchOptions.method ?? "GET",
      headers: this.buildHeaders(headers, skipAuthHeader),
      credentials: fetchOptions.credentials ?? "same-origin",
      body: data !== undefined ? JSON.stringify(data) : undefined,
    };

    try {
      const response = await fetch(url, init);
      if (
        response.status === 401 &&
        !skipAuthRefresh &&
        !path.startsWith("/api/auth/")
      ) {
        const refreshed = await this.refreshAccessToken();

        if (refreshed) {
          return this.request<T>(path, {
            ...options,
            skipAuthRefresh: true,
          });
        }
      }

      return this.parseResponse<T>(response);
    } catch (error) {
      console.error("[ApiClient] fetch error:", error);
      throw error;
    }
  }

  private async refreshAccessToken(): Promise<boolean> {
    const session = getStoredAuthSession();

    if (!session?.refreshToken) {
      clearStoredAuthSession();
      return false;
    }

    try {
      const response = await fetch(this.buildUrl("/api/auth/refresh"), {
        method: "POST",
        headers: this.buildHeaders(undefined, true),
        credentials: "same-origin",
        body: JSON.stringify({
          refresh_token: session.refreshToken,
        }),
      });

      if (!response.ok) {
        clearStoredAuthSession();
        return false;
      }

      const payload = await response.json();

      setStoredAuthSession({
        accessToken: payload.access_token,
        refreshToken: payload.refresh_token,
        user: payload.user,
      });

      return true;
    } catch (error) {
      console.error("[ApiClient] refresh error:", error);
      clearStoredAuthSession();
      return false;
    }
  }

  get<T = unknown>(path: string, query?: ApiQueryParams) {
    return this.request<T>(path, { method: "GET", query });
  }

  post<T = unknown>(path: string, data?: unknown) {
    return this.request<T>(path, { method: "POST", data });
  }

  put<T = unknown>(path: string, data?: unknown) {
    return this.request<T>(path, { method: "PUT", data });
  }

  patch<T = unknown>(path: string, data?: unknown) {
    return this.request<T>(path, { method: "PATCH", data });
  }

  delete<T = unknown>(path: string, data?: unknown) {
    return this.request<T>(path, { method: "DELETE", data });
  }
}

export const apiClient = new ApiClient();
