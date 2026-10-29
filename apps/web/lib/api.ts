export type ServiceStatus = "unknown" | "operational" | "degraded" | "down";
export type EventType = "check" | "incident";
export type EventStatus = "operational" | "degraded" | "down";

export type Service = {
  id: string;
  name: string;
  description: string | null;
  environment: string;
  status: ServiceStatus;
  created_at: string;
  updated_at: string;
};

export type ServiceEvent = {
  id: string;
  service_id: string;
  event_type: EventType;
  status: EventStatus;
  summary: string;
  details: string | null;
  occurred_at: string;
  resolved_at: string | null;
  created_at: string;
};

export type ServiceCreate = {
  name: string;
  description?: string;
  environment: string;
};

export type ServiceEventCreate = {
  event_type: EventType;
  status: EventStatus;
  summary: string;
  details?: string;
  occurred_at: string;
};

type ErrorBody = {
  error?: {
    code?: string;
    message?: string;
    details?: Array<{ msg?: string; loc?: Array<string | number> }>;
  };
};
type ErrorDetails = NonNullable<ErrorBody["error"]>["details"];

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details: ErrorDetails;

  constructor(status: number, code: string, message: string, details?: ErrorDetails) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

const apiBaseUrl = (process.env.NEXT_PUBLIC_API_BASE_URL || "/api-backend").replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl}${path}`, {
      ...init,
      headers: {
        Accept: "application/json",
        ...(init?.body ? { "Content-Type": "application/json" } : {}),
        ...init?.headers
      }
    });
  } catch {
    throw new ApiError(0, "network_error", "The API could not be reached. Check that the backend is running.");
  }

  const contentType = response.headers.get("content-type") || "";
  let body: unknown;
  try {
    body = contentType.includes("application/json") ? await response.json() : undefined;
  } catch {
    throw new ApiError(response.status, "invalid_response", "The API returned an unreadable response.");
  }

  if (!response.ok) {
    const errorBody = body as ErrorBody | undefined;
    throw new ApiError(
      response.status,
      errorBody?.error?.code || "http_error",
      errorBody?.error?.message || `The request failed with status ${response.status}.`,
      errorBody?.error?.details
    );
  }

  if (body === undefined) {
    throw new ApiError(response.status, "invalid_response", "The API returned an empty response.");
  }
  return body as T;
}

function assertArray<T>(value: unknown, resource: string): T[] {
  if (!Array.isArray(value)) {
    throw new ApiError(200, "invalid_response", `The API returned an invalid ${resource} response.`);
  }
  return value as T[];
}

function assertObject<T>(value: unknown, resource: string): T {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    throw new ApiError(200, "invalid_response", `The API returned an invalid ${resource} response.`);
  }
  return value as T;
}

export async function listServices(): Promise<Service[]> {
  return assertArray<Service>(await request("/services"), "service list");
}

export async function getService(serviceId: string): Promise<Service> {
  const service = (await listServices()).find((item) => item.id === serviceId);
  if (!service) {
    throw new ApiError(404, "not_found", "Service not found.");
  }
  return service;
}

export async function createService(data: ServiceCreate): Promise<Service> {
  return assertObject<Service>(await request("/services", {
    method: "POST",
    body: JSON.stringify(data)
  }), "service");
}

export async function getServiceEvents(serviceId: string): Promise<ServiceEvent[]> {
  return assertArray<ServiceEvent>(await request(`/services/${encodeURIComponent(serviceId)}/events`), "event history");
}

export async function createServiceEvent(serviceId: string, data: ServiceEventCreate): Promise<ServiceEvent> {
  return assertObject<ServiceEvent>(await request(`/services/${encodeURIComponent(serviceId)}/events`, {
    method: "POST",
    body: JSON.stringify(data)
  }), "event");
}

export async function resolveServiceEvent(serviceId: string, eventId: string): Promise<ServiceEvent> {
  return assertObject<ServiceEvent>(await request(
    `/services/${encodeURIComponent(serviceId)}/events/${encodeURIComponent(eventId)}/resolve`,
    { method: "POST" }
  ), "event");
}

export { request as apiRequest };
