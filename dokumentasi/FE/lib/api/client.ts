import type { ApiError } from "@/lib/api/types";

type RequestMethod = "GET" | "POST" | "PUT" | "DELETE";

type RequestOptions = {
  method?: RequestMethod;
  body?: BodyInit | Record<string, unknown> | null;
  headers?: HeadersInit;
  credentials?: RequestCredentials;
  csrfToken?: string;
  next?: NextFetchRequestConfig;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

export class ApiClientError extends Error {
  status: number;
  payload?: unknown;

  constructor(message: string, status: number, payload?: unknown) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.payload = payload;
  }
}

function buildHeaders(body: RequestOptions["body"], csrfToken?: string, headers?: HeadersInit) {
  const result = new Headers(headers);
  const isFormData = typeof FormData !== "undefined" && body instanceof FormData;

  if (!isFormData && body && !result.has("Content-Type")) {
    result.set("Content-Type", "application/json");
  }

  if (csrfToken && !result.has("X-CSRFToken")) {
    result.set("X-CSRFToken", csrfToken);
  }

  return result;
}

function serializeBody(body: RequestOptions["body"]) {
  if (!body) return undefined;
  const isNativeBody =
    body instanceof FormData ||
    body instanceof URLSearchParams ||
    body instanceof Blob ||
    typeof body === "string";

  if (isNativeBody) {
    return body;
  }

  return JSON.stringify(body);
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  const response = await fetch(url, {
    method: options.method ?? "GET",
    credentials: options.credentials ?? "include",
    headers: buildHeaders(options.body, options.csrfToken, options.headers),
    body: serializeBody(options.body),
    next: options.next,
  });

  const contentType = response.headers.get("content-type") ?? "";
  const isJson = contentType.includes("application/json");
  const payload = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    const message =
      typeof payload === "object" && payload && "detail" in payload
        ? String((payload as ApiError).detail)
        : response.statusText;
    throw new ApiClientError(message, response.status, payload);
  }

  return payload as T;
}

export { API_BASE_URL };
