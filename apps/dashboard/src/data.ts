import { z } from "zod";

const identifier = z.string().regex(/^[a-zA-Z0-9_-]+$/);
const status = z.enum(["complete", "active", "planned"]);
export const phaseSchema = z.object({
  id: identifier,
  number: z.string(),
  title: z.string(),
  status,
  summary: z.string(),
  exitCriterion: z.string(),
  milestones: z.array(z.object({ label: z.string(), status })),
});
export const workspaceSchema = z
  .object({
    schemaVersion: z.literal("1.0"),
    name: z.string(),
    description: z.string(),
    phases: z.array(phaseSchema).min(1),
    runs: z.array(
      z.object({
        id: identifier,
        label: z.string(),
        phaseId: identifier,
        seed: z.number().int(),
        kind: z.string(),
      }),
    ),
    evidence: z.array(
      z.object({
        title: z.string(),
        detail: z.string(),
        source: z.string(),
        status: z.enum(["verified", "pending", "limitation"]),
      }),
    ),
  })
  .superRefine((value, ctx) => {
    if (
      new Set(value.phases.map((p) => p.id)).size !== value.phases.length ||
      new Set(value.runs.map((r) => r.id)).size !== value.runs.length
    )
      ctx.addIssue({
        code: "custom",
        message: "Phase and run IDs must be unique.",
      });
    for (const run of value.runs)
      if (!value.phases.some((p) => p.id === run.phaseId))
        ctx.addIssue({
          code: "custom",
          message: "Run references an unknown phase.",
        });
  });
export const runSchema = z
  .object({
    schemaVersion: z.literal("1.0"),
    id: identifier,
    label: z.string(),
    seed: z.number().int(),
    simulator: z.string(),
    generatedAt: z.iso.datetime({ offset: true }),
    provenance: z.string(),
    channels: z
      .array(
        z.object({
          key: identifier,
          label: z.string(),
          unit: z.string(),
          role: z.enum(["state", "observation"]),
        }),
      )
      .min(1),
    samples: z.array(z.record(z.string(), z.number().finite())).min(2),
  })
  .superRefine((value, ctx) => {
    const keys = value.channels.map((c) => c.key);
    if (new Set(keys).size !== keys.length || keys.includes("time"))
      ctx.addIssue({
        code: "custom",
        message: "Channel keys must be unique and cannot be time.",
      });
    for (let i = 0; i < value.samples.length; i++) {
      const row = value.samples[i];
      if (
        row.time === undefined ||
        (i > 0 && row.time <= value.samples[i - 1].time) ||
        keys.some((k) => row[k] === undefined)
      ) {
        ctx.addIssue({
          code: "custom",
          message: "Samples need increasing time and every declared channel.",
        });
        break;
      }
    }
  });
export type Workspace = z.infer<typeof workspaceSchema>;
export type Phase = z.infer<typeof phaseSchema>;
export type Run = z.infer<typeof runSchema>;
export type Channel = Run["channels"][number];

export function normalizeEndpoint(input: string): string {
  const value = input.trim().replace(/\/+$/, "");
  if (!value) return "";
  const url = new URL(value);
  if (
    !["http:", "https:"].includes(url.protocol) ||
    url.username ||
    url.password ||
    url.search ||
    url.hash
  )
    throw new Error(
      "Use an HTTP(S) URL without credentials, query parameters, or fragments.",
    );
  return url.href.replace(/\/+$/, "");
}
export async function fetchJson(
  path: string,
  signal?: AbortSignal,
): Promise<unknown> {
  const response = await fetch(path, {
    signal: AbortSignal.any([
      AbortSignal.timeout(10000),
      ...(signal ? [signal] : []),
    ]),
    cache: "no-store",
  });
  if (!response.ok)
    throw new Error(`The data source returned HTTP ${response.status}.`);
  return response.json();
}
export function readSaved(key: string) {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}
export function save(key: string, value: string) {
  try {
    localStorage.setItem(key, value);
  } catch {
    /* Session still works without storage. */
  }
}
export function resourceUrl(base: string, resource: string) {
  return base ? `${base}/${resource}` : `/demo/${resource}.json`;
}
export function downloadRun(run: Run) {
  const keys = ["time", ...run.channels.map((c) => c.key)];
  const csv = [
    keys.join(","),
    ...run.samples.map((row) => keys.map((k) => row[k]).join(",")),
  ].join("\n");
  const url = URL.createObjectURL(
    new Blob([csv], { type: "text/csv;charset=utf-8" }),
  );
  const link = document.createElement("a");
  link.href = url;
  link.download = `${run.id}.csv`;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
