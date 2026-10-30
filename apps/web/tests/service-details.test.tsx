import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ServiceDetailsContent from "../app/services/[id]/details-content";
import {
  ApiError,
  createServiceEvent,
  getService,
  getServiceEvents,
  resolveServiceEvent
} from "../lib/api";

vi.mock("../lib/api", async () => {
  const actual = await vi.importActual<typeof import("../lib/api")>("../lib/api");
  return {
    ...actual,
    createServiceEvent: vi.fn(),
    getService: vi.fn(),
    getServiceEvents: vi.fn(),
    resolveServiceEvent: vi.fn()
  };
});

const mockedGetService = vi.mocked(getService);
const mockedGetServiceEvents = vi.mocked(getServiceEvents);
const mockedCreateServiceEvent = vi.mocked(createServiceEvent);
const mockedResolveServiceEvent = vi.mocked(resolveServiceEvent);

const service = {
  id: "service-1",
  name: "Payments",
  description: "Payment processing",
  environment: "production" as const,
  status: "operational" as const,
  created_at: "2026-10-29T18:00:00Z",
  updated_at: "2026-10-29T18:00:00Z"
};

const incident = {
  id: "event-1",
  service_id: "service-1",
  event_type: "incident" as const,
  status: "down" as const,
  summary: "Payments unavailable",
  details: "HTTP 503 responses",
  occurred_at: "2026-10-29T18:00:00Z",
  resolved_at: null,
  created_at: "2026-10-29T18:01:00Z"
};

function renderDetails() {
  return render(<ServiceDetailsContent id="service-1" />);
}

beforeEach(() => {
  mockedGetService.mockReset();
  mockedGetServiceEvents.mockReset();
  mockedCreateServiceEvent.mockReset();
  mockedResolveServiceEvent.mockReset();
});

describe("service details page", () => {
  it("loads and displays service information and event history", async () => {
    mockedGetService.mockResolvedValue(service);
    mockedGetServiceEvents.mockResolvedValue([incident]);

    renderDetails();

    expect(await screen.findByRole("heading", { name: "Payments" })).toBeInTheDocument();
    expect(screen.getByText("Payments unavailable")).toBeInTheDocument();
    expect(screen.getByText("incident · down")).toBeInTheDocument();
  });

  it("shows a not-found error for an unknown service", async () => {
    mockedGetService.mockRejectedValue(new ApiError(404, "not_found", "Service not found."));
    mockedGetServiceEvents.mockRejectedValue(new ApiError(404, "not_found", "Service not found."));

    renderDetails();

    expect(await screen.findByText("Service not found.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /try again/i })).toBeInTheDocument();
  });

  it("handles event-history failures without crashing", async () => {
    mockedGetService.mockResolvedValue(service);
    mockedGetServiceEvents.mockRejectedValue(new Error("History unavailable"));

    renderDetails();

    expect(await screen.findByText("Something went wrong. Please try again.")).toBeInTheDocument();
  });

  it("submits event data and shows the created event", async () => {
    mockedGetService.mockResolvedValue(service);
    mockedGetServiceEvents.mockResolvedValue([]);
    mockedCreateServiceEvent.mockResolvedValue({
      ...incident,
      event_type: "check",
      status: "degraded",
      summary: "Latency increased"
    });

    renderDetails();
    await screen.findByText(/no events recorded/i);
    fireEvent.click(screen.getByRole("button", { name: /record event/i }));
    fireEvent.change(screen.getByLabelText("Summary"), { target: { value: "Latency increased" } });
    fireEvent.change(screen.getByLabelText("Status"), { target: { value: "degraded" } });
    fireEvent.submit(screen.getByRole("heading", { name: /record a reliability event/i }).closest("form")!);

    await waitFor(() => {
      expect(mockedCreateServiceEvent).toHaveBeenCalledWith(
        "service-1",
        expect.objectContaining({
          event_type: "check",
          status: "degraded",
          summary: "Latency increased"
        })
      );
    });
    expect(await screen.findByText("Latency increased")).toBeInTheDocument();
  });

  it("shows event-creation failures", async () => {
    mockedGetService.mockResolvedValue(service);
    mockedGetServiceEvents.mockResolvedValue([]);
    mockedCreateServiceEvent.mockRejectedValue(new Error("Request failed"));

    renderDetails();
    await screen.findByText(/no events recorded/i);
    fireEvent.click(screen.getByRole("button", { name: /record event/i }));
    fireEvent.change(screen.getByLabelText("Summary"), { target: { value: "Latency increased" } });
    fireEvent.submit(screen.getByRole("heading", { name: /record a reliability event/i }).closest("form")!);

    expect(await screen.findByRole("alert")).toHaveTextContent(/something went wrong/i);
  });

  it("prevents repeated event submissions while pending", async () => {
    let resolveRequest!: (value: typeof incident) => void;
    mockedGetService.mockResolvedValue(service);
    mockedGetServiceEvents.mockResolvedValue([]);
    mockedCreateServiceEvent.mockReturnValue(new Promise((resolve) => {
      resolveRequest = resolve;
    }));

    renderDetails();
    await screen.findByText(/no events recorded/i);
    fireEvent.click(screen.getByRole("button", { name: /record event/i }));
    fireEvent.change(screen.getByLabelText("Summary"), { target: { value: "Latency increased" } });
    const submitButton = screen.getByRole("button", { name: /^record event$/i });
    fireEvent.click(submitButton);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /recording/i })).toBeDisabled();
    });
    fireEvent.click(submitButton);

    expect(mockedCreateServiceEvent).toHaveBeenCalledTimes(1);
    resolveRequest({ ...incident, summary: "Latency increased" });
    await screen.findByText("Latency increased");
  });

  it("resolves an incident and updates its history", async () => {
    mockedGetService.mockResolvedValue(service);
    mockedGetServiceEvents.mockResolvedValue([incident]);
    mockedResolveServiceEvent.mockResolvedValue({
      ...incident,
      resolved_at: "2026-10-29T19:00:00Z"
    });

    renderDetails();
    await screen.findByText("Payments unavailable");
    fireEvent.click(screen.getByRole("button", { name: /resolve incident/i }));

    await waitFor(() => {
      expect(mockedResolveServiceEvent).toHaveBeenCalledWith("service-1", "event-1");
    });
    expect(await screen.findByText(/resolved/i)).toBeInTheDocument();
  });

  it("shows resolution failures and disables the action while pending", async () => {
    let rejectRequest!: (reason?: unknown) => void;
    mockedGetService.mockResolvedValue(service);
    mockedGetServiceEvents.mockResolvedValue([incident]);
    mockedResolveServiceEvent.mockReturnValue(new Promise((_, reject) => {
      rejectRequest = reject;
    }));

    renderDetails();
    const resolveButton = await screen.findByRole("button", { name: /resolve incident/i });
    fireEvent.click(resolveButton);
    fireEvent.click(resolveButton);

    expect(mockedResolveServiceEvent).toHaveBeenCalledTimes(1);
    expect(resolveButton).toBeDisabled();
    rejectRequest(new Error("Conflict"));
    expect(await screen.findByRole("alert")).toHaveTextContent(/something went wrong/i);
  });
});
