import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Home from "../app/page";

describe("home page", () => {
  it("explains the journal purpose without implying live integration", () => {
    render(<Home />);

    expect(
      screen.getByRole("heading", { name: /service reliability, without the noise/i })
    ).toBeInTheDocument();
    expect(screen.getByText(/foundation is ready/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /cloudxzen home/i })).toHaveAttribute(
      "href",
      "/"
    );
  });
});
