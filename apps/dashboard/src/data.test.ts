import { describe, expect, it } from "vitest";
import {
  normalizeEndpoint,
  resourceUrl,
  runSchema,
  workspaceSchema,
} from "./data";
import workspace from "../public/demo/workspace.json";
import run from "../public/demo/runs/baseline-seed-42.json";

describe("research artifact boundary", () => {
  it("accepts the real exported simulation and registry", () => {
    expect(runSchema.parse(run).samples).toHaveLength(1150);
    expect(workspaceSchema.parse(workspace).phases).toHaveLength(12);
  });
  it("rejects missing channels, non-finite values and non-increasing time", () => {
    const missing = structuredClone(run);
    delete (missing.samples[0] as Record<string, number>).biomass;
    expect(runSchema.safeParse(missing).success).toBe(false);
    const invalid = structuredClone(run);
    invalid.samples[0].biomass = Infinity;
    expect(runSchema.safeParse(invalid).success).toBe(false);
    const time = structuredClone(run);
    time.samples[1].time = time.samples[0].time;
    expect(runSchema.safeParse(time).success).toBe(false);
  });
  it("rejects empty, duplicate and reserved channels", () => {
    expect(runSchema.safeParse({ ...run, samples: [] }).success).toBe(false);
    expect(
      runSchema.safeParse({
        ...run,
        channels: [...run.channels, run.channels[0]],
      }).success,
    ).toBe(false);
    expect(
      runSchema.safeParse({
        ...run,
        channels: [{ key: "time", label: "Bad", unit: "h", role: "state" }],
      }).success,
    ).toBe(false);
  });
  it("supports new phase results and channels without UI code changes", () => {
    const next = structuredClone(workspace);
    next.runs.push({
      id: "pid-42",
      label: "PID baseline",
      phaseId: "control",
      seed: 42,
      kind: "Controller comparison",
    });
    expect(workspaceSchema.safeParse(next).success).toBe(true);
    expect(
      runSchema.safeParse({
        ...run,
        channels: [
          ...run.channels,
          {
            key: "tracking_error",
            label: "Tracking error",
            unit: "g/L",
            role: "state",
          },
        ],
        samples: run.samples.map((s) => ({ ...s, tracking_error: 0.2 })),
      }).success,
    ).toBe(true);
  });
  it("rejects duplicate phase IDs and unknown run phase references", () => {
    expect(
      workspaceSchema.safeParse({
        ...workspace,
        phases: [...workspace.phases, workspace.phases[0]],
      }).success,
    ).toBe(false);
    expect(
      workspaceSchema.safeParse({
        ...workspace,
        runs: [{ ...workspace.runs[0], phaseId: "unknown" }],
      }).success,
    ).toBe(false);
  });
  it("allows an empty run registry for future workspaces", () => {
    expect(workspaceSchema.safeParse({ ...workspace, runs: [] }).success).toBe(
      true,
    );
  });
});

describe("configurable source", () => {
  it("normalizes URLs and resolves equivalent API and static resources", () => {
    expect(normalizeEndpoint(" http://localhost:8000/api/v1/// ")).toBe(
      "http://localhost:8000/api/v1",
    );
    expect(normalizeEndpoint("")).toBe("");
    expect(resourceUrl("", "runs/baseline-seed-42")).toBe(
      "/demo/runs/baseline-seed-42.json",
    );
    expect(resourceUrl("http://localhost:8000/api/v1", "workspace")).toBe(
      "http://localhost:8000/api/v1/workspace",
    );
  });
  it("rejects unsupported protocols and embedded credentials", () => {
    for (const value of [
      "file:///etc/passwd",
      "javascript:alert(1)",
      "https://user:pass@example.com",
      "https://example.com?token=abc",
      "https://example.com#hash",
    ])
      expect(() => normalizeEndpoint(value)).toThrow();
  });
});
