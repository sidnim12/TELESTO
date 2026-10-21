// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import App from "./App";
import workspace from "../public/demo/workspace.json";
import run from "../public/demo/runs/baseline-seed-42.json";

vi.mock("./TrajectoryChart", () => ({
  default: () => <div data-testid="chart">Trajectory chart</div>,
}));

beforeEach(() => {
  localStorage.clear();
  location.hash = "";
  document.documentElement.dataset.theme = "light";
  vi.stubGlobal("scrollTo", vi.fn());
  HTMLDialogElement.prototype.showModal = function () {
    this.setAttribute("open", "");
  };
  HTMLDialogElement.prototype.close = function () {
    this.removeAttribute("open");
  };
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string) => {
      if (url === "/config.json")
        return { ok: true, json: async () => ({ apiBaseUrl: "" }) };
      if (url === "/demo/workspace.json")
        return { ok: true, json: async () => workspace };
      if (url === "/demo/runs/baseline-seed-42.json")
        return { ok: true, json: async () => run };
      return { ok: false, status: 503 };
    }),
  );
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

async function ready() {
  render(<App />);
  await screen.findByTestId("chart");
}

describe("observatory interactions", () => {
  it("collapses to the four-section icon rail and remembers the preference", async () => {
    await ready();
    const navigation = screen.getByRole("navigation", {
      name: "Main navigation",
    });
    expect(
      within(navigation)
        .getAllByRole("link")
        .map((link) => link.getAttribute("aria-label")),
    ).toEqual([
      "Overview",
      "Digital twin",
      "Research roadmap",
      "Evidence library",
    ]);
    fireEvent.click(screen.getByRole("button", { name: "Collapse sidebar" }));
    expect(
      screen
        .getByRole("button", { name: "Expand sidebar" })
        .getAttribute("aria-expanded"),
    ).toBe("false");
    expect(localStorage.getItem("telesto-sidebar")).toBe("collapsed");
    fireEvent.click(
      within(navigation).getByRole("link", { name: "Evidence library" }),
    );
    expect(
      screen.getByRole("heading", { name: "Every claim has a source." }),
    ).toBeTruthy();
    cleanup();
    render(<App />);
    expect(screen.getByRole("button", { name: "Expand sidebar" })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Expand sidebar" }));
    expect(localStorage.getItem("telesto-sidebar")).toBe("expanded");
  });
  it("opens the mobile menu and closes it on selection or Escape", async () => {
    await ready();
    const trigger = screen.getByRole("button", { name: "Open navigation" });
    fireEvent.click(trigger);
    expect(trigger.getAttribute("aria-expanded")).toBe("true");
    fireEvent.click(screen.getByRole("link", { name: "Digital twin" }));
    expect(trigger.getAttribute("aria-expanded")).toBe("false");
    fireEvent.click(trigger);
    fireEvent.keyDown(window, { key: "Escape" });
    expect(trigger.getAttribute("aria-expanded")).toBe("false");
  });
  it("loads real results, switches theme and persists the choice", async () => {
    await ready();
    expect(screen.getByText("1,150")).toBeTruthy();
    fireEvent.click(
      screen.getByRole("button", { name: "Switch to dark theme" }),
    );
    expect(document.documentElement.dataset.theme).toBe("dark");
    expect(localStorage.getItem("telesto-theme")).toBe("dark");
  });
  it("resets, plays, pauses and scrubs recorded samples", async () => {
    await ready();
    const slider = screen.getByRole("slider", {
      name: "Replay position",
    }) as HTMLInputElement;
    expect(slider.value).toBe("1149");
    fireEvent.click(screen.getByRole("button", { name: "Reset replay" }));
    expect(slider.value).toBe("0");
    fireEvent.click(screen.getByRole("button", { name: "Play replay" }));
    await waitFor(() => expect(Number(slider.value)).toBeGreaterThan(0));
    fireEvent.click(screen.getByRole("button", { name: "Pause replay" }));
    fireEvent.change(slider, { target: { value: "500" } });
    expect(slider.value).toBe("500");
    expect(screen.getByRole("button", { name: "Play replay" })).toBeTruthy();
  });
  it("opens future phases without inventing results", async () => {
    await ready();
    fireEvent.click(screen.getByRole("link", { name: "Research roadmap" }));
    fireEvent.click(
      screen.getByRole("button", {
        name: "Phase 02: Control baselines, planned",
      }),
    );
    expect(
      screen.getByText("No results published for this phase yet."),
    ).toBeTruthy();
    expect(
      screen.getByText(
        "Recipe, PID, and MPC baselines run under one evaluation protocol.",
      ),
    ).toBeTruthy();
  });
  it("switches variables and presents seven process channels", async () => {
    await ready();
    fireEvent.click(screen.getByRole("link", { name: "Digital twin" }));
    fireEvent.change(
      screen.getByRole("combobox", { name: "Trajectory variable" }),
      { target: { value: "temperature" } },
    );
    expect(
      (
        screen.getByRole("combobox", {
          name: "Trajectory variable",
        }) as HTMLSelectElement
      ).value,
    ).toBe("temperature");
    expect(screen.getAllByText("Observation channel")).toHaveLength(5);
    expect(screen.getAllByText("Internal process state")).toHaveLength(2);
  });
  it("shows API failure explicitly and recovers to bundled data", async () => {
    await ready();
    fireEvent.click(
      screen.getByRole("button", { name: "Connection settings" }),
    );
    fireEvent.click(screen.getByRole("radio", { name: /Connect an API/ }));
    fireEvent.click(screen.getByRole("button", { name: "Apply connection" }));
    await screen.findByRole("alert");
    expect(screen.queryByTestId("chart")).toBeNull();
    expect(localStorage.getItem("telesto-endpoint")).toBe(
      "http://127.0.0.1:8000/api/v1",
    );
    fireEvent.click(
      screen.getByRole("button", { name: "Use bundled simulation" }),
    );
    await screen.findByTestId("chart");
    expect(localStorage.getItem("telesto-endpoint")).toBe("");
  });
  it("handles an empty run registry without an endless loader", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string) => ({
        ok: true,
        json: async () =>
          url === "/config.json"
            ? { apiBaseUrl: "" }
            : { ...workspace, runs: [] },
      })),
    );
    render(<App />);
    await screen.findByText("No runs published yet");
    expect(
      (screen.getByRole("button", { name: "Export CSV" }) as HTMLButtonElement)
        .disabled,
    ).toBe(true);
  });
  it("rejects credentials in endpoint URLs without applying them", async () => {
    await ready();
    fireEvent.click(
      screen.getByRole("button", { name: "Connection settings" }),
    );
    fireEvent.click(screen.getByRole("radio", { name: /Connect an API/ }));
    fireEvent.change(screen.getByRole("textbox", { name: /API base URL/ }), {
      target: { value: "https://user:pass@example.com/api/v1" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Apply connection" }));
    expect(
      await within(screen.getByRole("dialog")).findByRole("alert"),
    ).toBeTruthy();
    expect(localStorage.getItem("telesto-endpoint")).toBeNull();
  });
});
