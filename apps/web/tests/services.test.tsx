import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ServicesPage from "../app/services/page";
import { listServices } from "../lib/api";

vi.mock("../lib/api", async () => {
  const actual = await vi.importActual<typeof import("../lib/api")>("../lib/api");
  return { ...actual, listServices: vi.fn() };
});

const mockedListServices = vi.mocked(listServices);

beforeEach(() => {
  mockedListServices.mockReset();
});

describe("services page", () => {
  it("renders a successful service list", async () => {
    mockedListServices.mockResolvedValue([{
      id: "service-1",
      name: "Payments",
      description: "Payment processing",
      environment: "production",
      status: "operational",
      created_at: "2026-10-29T18:00:00Z",
      updated_at: "2026-10-29T18:00:00Z"
    }]);

    render(<ServicesPage />);

    expect(await screen.findByRole("heading", { name: "Payments" })).toBeInTheDocument();
    expect(screen.getByText("operational")).toBeInTheDocument();
  });

  it("renders the empty state", async () => {
    mockedListServices.mockResolvedValue([]);

    render(<ServicesPage />);

    expect(await screen.findByText(/no services registered yet/i)).toBeInTheDocument();
  });

  it("renders a retryable error state", async () => {
    mockedListServices.mockRejectedValue(new Error("offline"));

    render(<ServicesPage />);

    expect(await screen.findByText(/something went wrong/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /try again/i })).toBeInTheDocument();
  });

  it("validates registration before submitting", async () => {
    mockedListServices.mockResolvedValue([]);

    render(<ServicesPage />);
    await screen.findByText(/no services registered yet/i);
    fireEvent.click(screen.getByRole("button", { name: /^register service$/i }));
    fireEvent.click(screen.getByRole("button", { name: /^register service$/i }));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(/name and environment are required/i);
    });
  });
});
