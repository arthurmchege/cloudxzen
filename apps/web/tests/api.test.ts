import { afterEach, describe, expect, it, vi } from "vitest";

import {
  ApiError,
  createService,
  createServiceEvent,
  listServices,
  resolveServiceEvent
} from "../lib/api";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("API client", () => {
  it("parses a successful service list", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify([{ id: "service-1", name: "Payments" }]), {
          status: 200,
          headers: { "content-type": "application/json" }
        })
      )
    );

    await expect(listServices()).resolves.toEqual([{ id: "service-1", name: "Payments" }]);
  });

  it("preserves structured backend validation errors", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({
          error: {
            code: "validation_error",
            message: "Request validation failed.",
            details: [{ msg: "must not be blank" }]
          }
        }), {
          status: 422,
          headers: { "content-type": "application/json" }
        })
      )
    );

    await expect(createService({ name: "", environment: "production" })).rejects.toMatchObject({
      status: 422,
      code: "validation_error",
      message: "Request validation failed."
    });
  });

  it("turns network failures into a user-readable API error", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("offline")));

    await expect(listServices()).rejects.toMatchObject({
      status: 0,
      code: "network_error"
    });
  });

  it("rejects malformed successful responses", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ services: [] }), {
          status: 200,
          headers: { "content-type": "application/json" }
        })
      )
    );

    await expect(listServices()).rejects.toMatchObject({
      status: 200,
      code: "invalid_response"
    } satisfies Partial<ApiError>);
  });

  it("sends supported event data and parses the created event", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ id: "event-1", event_type: "check" }), {
        status: 201,
        headers: { "content-type": "application/json" }
      })
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(createServiceEvent("service-1", {
      event_type: "check",
      status: "operational",
      summary: "Health check passed",
      occurred_at: "2026-10-29T18:00:00.000Z"
    })).resolves.toMatchObject({ id: "event-1" });
    expect(fetchMock).toHaveBeenCalledWith(
      "/api-backend/services/service-1/events",
      expect.objectContaining({ method: "POST" })
    );
  });

  it("uses the incident resolution endpoint", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ id: "event-1", resolved_at: "2026-10-29T19:00:00Z" }), {
          status: 200,
          headers: { "content-type": "application/json" }
        })
      )
    );

    await expect(resolveServiceEvent("service-1", "event-1")).resolves.toMatchObject({
      resolved_at: "2026-10-29T19:00:00Z"
    });
  });
});
