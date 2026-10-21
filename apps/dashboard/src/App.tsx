import { lazy, Suspense, useEffect, useRef, useState } from "react";
import {
  Activity,
  ArrowDownToLine,
  ArrowRight,
  ArrowUpRight,
  BookOpen,
  Check,
  CheckCheck,
  ChevronDown,
  ChevronRight,
  Circle,
  CircleDot,
  Database,
  FlaskConical,
  Layers3,
  LayoutDashboard,
  Menu,
  Moon,
  Network,
  Pause,
  PanelLeftClose,
  PanelLeftOpen,
  Play,
  Radio,
  RefreshCw,
  RotateCcw,
  ShieldCheck,
  Sun,
  X,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import {
  downloadRun,
  fetchJson,
  normalizeEndpoint,
  readSaved,
  resourceUrl,
  runSchema,
  save,
  workspaceSchema,
} from "./data";
import type { Phase, Run, Workspace } from "./data";
import Reactor from "./Reactor";

const TrajectoryChart = lazy(() => import("./TrajectoryChart"));
type View = "overview" | "twin" | "roadmap" | "evidence";
const navItems: { id: View; label: string; icon: LucideIcon }[] = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "twin", label: "Digital twin", icon: FlaskConical },
  { id: "roadmap", label: "Research roadmap", icon: Network },
  { id: "evidence", label: "Evidence library", icon: BookOpen },
];
const format = (n: number, digits = 2) =>
  n.toLocaleString("en-US", {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  });
function currentView(): View {
  const hash = location.hash.slice(1);
  return navItems.some((n) => n.id === hash) ? (hash as View) : "overview";
}
function Status({ value }: { value: Phase["status"] }) {
  return (
    <span className={`status ${value}`}>
      <i />
      {value === "active"
        ? "In progress"
        : value === "complete"
          ? "Complete"
          : "Planned"}
    </span>
  );
}

export default function App() {
  const [view, setView] = useState<View>(currentView);
  const [theme, setTheme] = useState(
    document.documentElement.dataset.theme || "light",
  );
  const [menu, setMenu] = useState(false);
  const [collapsed, setCollapsed] = useState(
    () => readSaved("telesto-sidebar") === "collapsed",
  );
  const [settings, setSettings] = useState(false);
  const [base, setBase] = useState<string | null>(null);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [run, setRun] = useState<Run | null>(null);
  const [runId, setRunId] = useState("");
  const [error, setError] = useState("");
  const [runError, setRunError] = useState("");
  const [reload, setReload] = useState(0);
  const [cursor, setCursor] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [metric, setMetric] = useState("biomass");
  const [phaseId, setPhaseId] = useState("");
  const [toast, setToast] = useState("");

  useEffect(() => {
    const handle = () => setView(currentView());
    window.addEventListener("hashchange", handle);
    return () => window.removeEventListener("hashchange", handle);
  }, []);
  useEffect(() => {
    const controller = new AbortController();
    const stored = readSaved("telesto-endpoint");
    if (stored !== null) {
      try {
        setBase(normalizeEndpoint(stored));
      } catch {
        setBase("");
      }
      return;
    }
    fetchJson("/config.json", controller.signal)
      .then((config) => {
        const configured = (config as { apiBaseUrl?: string }).apiBaseUrl ?? "";
        setBase(normalizeEndpoint(configured));
      })
      .catch((e) => {
        if (!controller.signal.aborted) {
          setError(`Unable to load runtime configuration: ${e.message}`);
        }
      });
    return () => controller.abort();
  }, []);
  useEffect(() => {
    if (base === null) return;
    const controller = new AbortController();
    setWorkspace(null);
    setRun(null);
    setPlaying(false);
    setError("");
    setRunError("");
    fetchJson(resourceUrl(base, "workspace"), controller.signal)
      .then((raw) => {
        const data = workspaceSchema.parse(raw);
        setWorkspace(data);
        setRunId(data.runs[0]?.id ?? "");
        setPhaseId(
          data.phases.find((p) => p.status === "active")?.id ??
            data.phases[0].id,
        );
      })
      .catch((e) => {
        if (!controller.signal.aborted)
          setError(
            e instanceof Error ? e.message : "Unable to load workspace.",
          );
      });
    return () => controller.abort();
  }, [base, reload]);
  useEffect(() => {
    if (!workspace || !runId || base === null) return;
    const controller = new AbortController();
    setRun(null);
    setPlaying(false);
    setRunError("");
    fetchJson(resourceUrl(base, `runs/${runId}`), controller.signal)
      .then((raw) => {
        const data = runSchema.parse(raw);
        if (data.id !== runId)
          throw new Error("The data source returned the wrong run.");
        setRun(data);
        setCursor(data.samples.length - 1);
        setMetric(data.channels[0].key);
      })
      .catch((e) => {
        if (!controller.signal.aborted)
          setRunError(e instanceof Error ? e.message : "Unable to load run.");
      });
    return () => controller.abort();
  }, [workspace, base, runId]);
  useEffect(() => {
    if (!playing || !run) return;
    const timer = window.setInterval(
      () =>
        setCursor((i) =>
          Math.min(
            i + Math.max(1, Math.round(run.samples.length / 160)),
            run.samples.length - 1,
          ),
        ),
      100,
    );
    return () => clearInterval(timer);
  }, [playing, run]);
  useEffect(() => {
    if (run && cursor >= run.samples.length - 1) setPlaying(false);
  }, [cursor, run]);
  useEffect(() => {
    if (!toast) return;
    const id = setTimeout(() => setToast(""), 3000);
    return () => clearTimeout(id);
  }, [toast]);
  useEffect(() => {
    if (!menu) return;
    const dismiss = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMenu(false);
    };
    window.addEventListener("keydown", dismiss);
    return () => window.removeEventListener("keydown", dismiss);
  }, [menu]);

  function navigate(next: View) {
    location.hash = next;
    setView(next);
    setMenu(false);
    setPlaying(false);
    window.scrollTo({ top: 0, behavior: "instant" });
  }
  function toggleTheme() {
    const next = theme === "light" ? "dark" : "light";
    setTheme(next);
    document.documentElement.dataset.theme = next;
    save("telesto-theme", next);
  }
  function changeEndpoint(next: string) {
    save("telesto-endpoint", next);
    setBase(next);
    setReload((n) => n + 1);
    setSettings(false);
  }
  const active = workspace?.phases.find((p) => p.status === "active");
  const selectedPhase = workspace?.phases.find((p) => p.id === phaseId);
  const channel =
    run?.channels.find((c) => c.key === metric) ?? run?.channels[0];
  const sample = run?.samples[cursor];
  const completed =
    workspace?.phases.filter((p) => p.status === "complete").length ?? 0;

  function trajectory(expanded = false) {
    return (
      <section
        className={`panel trajectory-panel ${expanded ? "expanded" : ""}`}
        aria-label="Batch trajectory"
      >
        <div className="panel-heading">
          <div>
            <span className="eyebrow">THE PROCESS, OBSERVED</span>
            <h2>
              Batch trajectory <span className="tiny-tag">REPLAY</span>
            </h2>
          </div>
          <button
            className="icon-button"
            aria-label="Export trajectory CSV"
            disabled={!run}
            onClick={() => {
              if (run) {
                downloadRun(run);
                setToast("Trajectory CSV exported");
              }
            }}
          >
            <ArrowDownToLine size={17} />
          </button>
        </div>
        {run && channel && sample ? (
          <>
            <div className="chart-toolbar">
              <div>
                <span className="chart-value">
                  {format(sample[channel.key])}
                </span>
                <span className="unit">{channel.unit}</span>
                <span className="chart-caption">
                  {channel.label} at {format(sample.time, 1)} h
                </span>
              </div>
              <label className="select-wrap">
                <span className="sr-only">Trajectory variable</span>
                <select
                  value={metric}
                  onChange={(e) => setMetric(e.target.value)}
                >
                  {run.channels.map((c) => (
                    <option key={c.key} value={c.key}>
                      {c.label}
                    </option>
                  ))}
                </select>
                <ChevronDown size={13} />
              </label>
            </div>
            <Suspense
              fallback={
                <div className="chart skeleton" aria-label="Loading chart" />
              }
            >
              <TrajectoryChart run={run} channel={channel} cursor={cursor} />
            </Suspense>
            <div className="playback">
              <button
                className="play-button"
                aria-label={playing ? "Pause replay" : "Play replay"}
                onClick={() => {
                  if (cursor >= run.samples.length - 1) setCursor(0);
                  setPlaying(!playing);
                }}
              >
                {playing ? <Pause size={14} /> : <Play size={14} />}
              </button>
              <button
                className="icon-button reset"
                aria-label="Reset replay"
                onClick={() => {
                  setCursor(0);
                  setPlaying(false);
                }}
              >
                <RotateCcw size={14} />
              </button>
              <input
                type="range"
                aria-label="Replay position"
                min="0"
                max={run.samples.length - 1}
                value={cursor}
                onChange={(e) => {
                  setCursor(Number(e.target.value));
                  setPlaying(false);
                }}
              />
              <span className="mono playback-time">
                {format(sample.time, 1)} / {format(run.samples.at(-1)!.time, 1)}{" "}
                h
              </span>
            </div>
            <div className="panel-foot">
              <span>
                <i className="dot copper" />
                {run.simulator} · Seed {run.seed}
              </span>
              <span>
                {run.samples.length.toLocaleString()} samples · Precomputed
                replay
              </span>
            </div>
          </>
        ) : runError ? (
          <div className="empty-state">
            <Database />
            <h3>Run could not be loaded</h3>
            <p>
              {runError.length > 250
                ? "The run does not match the supported data contract."
                : runError}
            </p>
            <button
              className="button secondary"
              onClick={() => setReload((n) => n + 1)}
            >
              Retry data source
            </button>
          </div>
        ) : workspace?.runs.length === 0 ? (
          <div className="empty-state">
            <FlaskConical />
            <h3>No runs published yet</h3>
            <p>
              Results will appear here when a run is added to this workspace.
            </p>
          </div>
        ) : (
          <div className="chart skeleton" aria-label="Loading trajectory" />
        )}
      </section>
    );
  }

  return (
    <div className={`app-shell ${collapsed ? "sidebar-collapsed" : ""}`}>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <button
        className={`sidebar-scrim ${menu ? "is-visible" : ""}`}
        aria-label="Dismiss navigation overlay"
        tabIndex={-1}
        aria-hidden={!menu}
        onClick={() => setMenu(false)}
      />
      <aside
        id="workspace-sidebar"
        className={`sidebar ${menu ? "is-open" : ""}`}
      >
        <div className="sidebar-heading">
          <a
            className="brand"
            href="#overview"
            onClick={() => navigate("overview")}
            aria-label="TELESTO overview"
          >
            <span className="brand-symbol">
              <span />T
            </span>
            <span className="brand-wordmark">
              TELESTO<span className="brand-sub">RESEARCH OBSERVATORY</span>
            </span>
          </a>
          <button
            className="icon-button sidebar-toggle"
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            aria-expanded={!collapsed}
            aria-controls="workspace-navigation"
            onClick={() => {
              setCollapsed(!collapsed);
              save("telesto-sidebar", collapsed ? "expanded" : "collapsed");
            }}
          >
            {collapsed ? (
              <PanelLeftOpen size={18} />
            ) : (
              <PanelLeftClose size={18} />
            )}
          </button>
          <button
            className="icon-button sidebar-mobile-close"
            aria-label="Close navigation"
            onClick={() => setMenu(false)}
          >
            <X size={18} />
          </button>
        </div>
        <span className="nav-caption">WORKSPACE</span>
        <nav id="workspace-navigation" aria-label="Main navigation">
          {navItems.map(({ id, label, icon: Icon }) => (
            <a
              href={`#${id}`}
              key={id}
              className={`nav-item ${view === id ? "selected" : ""}`}
              aria-current={view === id ? "page" : undefined}
              aria-label={label}
              onClick={(e) => {
                e.preventDefault();
                navigate(id);
              }}
            >
              <Icon size={18} />
              <span className="nav-label">{label}</span>
              <span className="nav-tooltip" aria-hidden="true">
                {label}
              </span>
              {view === id && <span className="nav-active-dot" />}
            </a>
          ))}
        </nav>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div className="breadcrumb">
            <button
              className="icon-button mobile-menu"
              aria-label="Open navigation"
              aria-expanded={menu}
              aria-controls="workspace-sidebar"
              onClick={() => setMenu(true)}
            >
              <Menu size={20} />
            </button>
            <span>Workspace</span>
            <ChevronRight size={13} />
            <strong>{navItems.find((n) => n.id === view)?.label}</strong>
          </div>
          <div className="topbar-actions">
            <button
              className="source-pill"
              aria-label="Connection settings"
              title="Connection settings"
              onClick={() => setSettings(true)}
            >
              <i className={`dot ${base ? "green" : "copper"}`} />
              {base ? "API source" : "Bundled simulation"}
              <ChevronDown size={12} />
            </button>
            <span className="topbar-divider" />
            <button
              className="icon-button"
              onClick={toggleTheme}
              aria-label={`Switch to ${theme === "light" ? "dark" : "light"} theme`}
            >
              {theme === "light" ? <Moon size={18} /> : <Sun size={18} />}
            </button>
          </div>
        </header>
        <main id="main" tabIndex={-1}>
          <div className="page-heading">
            <div>
              <div className="eyebrow page-eyebrow">
                <span className="short-line" /> SCALE-ADAPTIVE INTELLIGENCE
              </div>
              <h1>
                {view === "overview"
                  ? "The bigger picture."
                  : view === "twin"
                    ? "A window into the process."
                    : view === "roadmap"
                      ? "Built on evidence. In phases."
                      : "Every claim has a source."}
              </h1>
              <p>
                {view === "overview"
                  ? "From a reproducible process world to better biological decisions."
                  : view === "twin"
                    ? "Explore the baseline, one observation at a time."
                    : view === "roadmap"
                      ? "A deliberate path from simulation to adaptive decision-making."
                      : "What is established, what is pending, and where the boundaries are."}
              </p>
            </div>
            <button
              className="button secondary heading-button"
              onClick={() => {
                if (run) {
                  downloadRun(run);
                  setToast("Trajectory CSV exported");
                }
              }}
              disabled={!run}
            >
              <ArrowDownToLine size={15} />
              Export CSV
            </button>
          </div>
          {error ? (
            <section className="panel empty-state error-state" role="alert">
              <Database size={28} />
              <h2>We couldn’t reach your workspace.</h2>
              <p>
                {error.length > 250
                  ? "The source returned data that does not match schema version 1.0."
                  : error}
              </p>
              <div className="button-row">
                <button
                  className="button primary"
                  onClick={() =>
                    base === null ? location.reload() : setReload((n) => n + 1)
                  }
                >
                  <RefreshCw size={15} />
                  Retry
                </button>
                <button
                  className="button secondary"
                  onClick={() => changeEndpoint("")}
                >
                  Use bundled simulation
                </button>
                <button
                  className="text-button"
                  onClick={() => setSettings(true)}
                >
                  Change source
                </button>
              </div>
            </section>
          ) : !workspace ? (
            <div className="loading-workspace" role="status">
              <div className="skeleton hero-skeleton" />
              <p>Preparing the observatory…</p>
            </div>
          ) : (
            <>
              {view === "overview" && (
                <>
                  <section className="hero">
                    <div className="hero-copy">
                      <span className="hero-kicker">
                        <i className="dot" /> RESEARCH IN MOTION
                      </span>
                      <h2>
                        Learn the process.
                        <br />
                        <em>Then decide.</em>
                      </h2>
                      <p>
                        Understanding how biological systems change
                        <br className="desktop-break" /> as they scale. Starting
                        with fermentation.
                      </p>
                      <div className="hero-actions">
                        <button
                          className="button hero-button"
                          onClick={() => navigate("twin")}
                        >
                          Explore the digital twin <ArrowUpRight size={16} />
                        </button>
                        <button
                          className="hero-link"
                          onClick={() => navigate("roadmap")}
                        >
                          Our research path <ArrowRight size={15} />
                        </button>
                      </div>
                      <div className="hero-meta">
                        <span>01 / FIRST RESEARCH DOMAIN</span>
                        <span>FED-BATCH FERMENTATION</span>
                      </div>
                    </div>
                    <Reactor />
                  </section>
                  <section
                    className="stats-grid"
                    aria-label="Workspace summary"
                  >
                    <Stat
                      label="CURRENT MILESTONE"
                      icon={Layers3}
                      value={active ? `Phase ${active.number}` : "All phases"}
                      detail={active?.title ?? "Research progression"}
                    />
                    <Stat
                      label="SIMULATED DURATION"
                      icon={Activity}
                      value={
                        run
                          ? format(
                              run.samples.at(-1)!.time - run.samples[0].time,
                              1,
                            )
                          : "—"
                      }
                      unit="h"
                      detail="Complete baseline batch"
                    />
                    <Stat
                      label="RECORDED SAMPLES"
                      icon={Database}
                      value={run ? run.samples.length.toLocaleString() : "—"}
                      detail={
                        run
                          ? `${run.channels.length} process variables captured`
                          : "Waiting for published results"
                      }
                    />
                    <Stat
                      label="REPRODUCIBLE BY DESIGN"
                      icon={CheckCheck}
                      value={run ? `Seed ${run.seed}` : "—"}
                      detail="Deterministic baseline configuration"
                    />
                  </section>
                  <div className="overview-grid">
                    {trajectory()}
                    <section className="panel milestone-panel">
                      <div className="panel-heading">
                        <div>
                          <span className="eyebrow">WHERE WE ARE</span>
                          <h2>Environment first.</h2>
                        </div>
                        <span className="phase-glyph">
                          {active?.number ?? "✓"}
                        </span>
                      </div>
                      {active && (
                        <>
                          <div className="milestone-intro">
                            <Status value={active.status} />
                            <p>{active.summary}</p>
                          </div>
                          <ul className="milestone-list">
                            {active.milestones.map((m) => (
                              <li key={m.label} className={m.status}>
                                {m.status === "complete" ? (
                                  <Check size={14} />
                                ) : m.status === "active" ? (
                                  <CircleDot size={14} />
                                ) : (
                                  <Circle size={14} />
                                )}
                                <span>{m.label}</span>
                              </li>
                            ))}
                          </ul>
                        </>
                      )}
                      <button
                        className="panel-link"
                        onClick={() => navigate("roadmap")}
                      >
                        View research roadmap <ArrowRight size={15} />
                      </button>
                    </section>
                  </div>
                  <section className="next-section">
                    <div className="section-title">
                      <div>
                        <span className="eyebrow">THE NEXT HORIZON</span>
                        <h2>From simulation to understanding.</h2>
                      </div>
                      <button
                        className="text-button"
                        onClick={() => navigate("roadmap")}
                      >
                        All phases <ArrowRight size={15} />
                      </button>
                    </div>
                    <div className="future-grid">
                      {workspace.phases
                        .filter((p) => p.status === "planned")
                        .slice(0, 3)
                        .map((p) => (
                          <button
                            className="future-card"
                            key={p.id}
                            onClick={() => {
                              setPhaseId(p.id);
                              navigate("roadmap");
                            }}
                          >
                            <div className="future-card-top">
                              <span className="mono">PHASE {p.number}</span>
                              <ArrowUpRight size={18} />
                            </div>
                            <h3>{p.title}</h3>
                            <p>{p.summary}</p>
                            <Status value={p.status} />
                          </button>
                        ))}
                    </div>
                  </section>
                </>
              )}
              {view === "twin" && (
                <>
                  <div className="twin-banner">
                    <div>
                      <Radio size={18} />
                      <span>Baseline replay</span>
                      <span className="subtle">
                        Recorded simulation · no actuator control
                      </span>
                    </div>
                    <label className="select-wrap">
                      <span className="sr-only">Select run</span>
                      <select
                        value={runId}
                        disabled={!workspace.runs.length}
                        onChange={(e) => setRunId(e.target.value)}
                      >
                        {workspace.runs.map((r) => (
                          <option key={r.id} value={r.id}>
                            {r.label} · seed {r.seed}
                          </option>
                        ))}
                        {!workspace.runs.length && <option>No runs</option>}
                      </select>
                      <ChevronDown size={13} />
                    </label>
                  </div>
                  {trajectory(true)}
                  {run && sample && (
                    <>
                      <div className="section-title space-top">
                        <div>
                          <span className="eyebrow">PROCESS SNAPSHOT</span>
                          <h2>At {format(sample.time, 1)} simulated hours.</h2>
                        </div>
                        <span className="mono subtle">
                          SAMPLE {cursor + 1} / {run.samples.length}
                        </span>
                      </div>
                      <div className="channel-grid">
                        {run.channels.map((c) => (
                          <button
                            key={c.key}
                            className={`channel-card ${metric === c.key ? "chosen" : ""}`}
                            onClick={() => setMetric(c.key)}
                            aria-pressed={metric === c.key}
                          >
                            <span>
                              {c.label}
                              <ArrowUpRight size={14} />
                            </span>
                            <strong>
                              {format(sample[c.key])}
                              <small>{c.unit}</small>
                            </strong>
                            <span className="channel-role">
                              {c.role === "state"
                                ? "Internal process state"
                                : "Observation channel"}
                            </span>
                          </button>
                        ))}
                      </div>
                      <div className="provenance-note">
                        <ShieldCheck size={20} />
                        <div>
                          <strong>
                            Reproducible, with explicit boundaries.
                          </strong>
                          <p>{run.provenance}</p>
                          <span className="mono">
                            EXPORTED{" "}
                            {new Date(run.generatedAt).toLocaleString()} ·{" "}
                            {run.id}
                          </span>
                        </div>
                      </div>
                    </>
                  )}
                </>
              )}
              {view === "roadmap" && (
                <>
                  <div className="roadmap-summary">
                    <span>
                      <strong>{completed.toString().padStart(2, "0")}</strong>{" "}
                      complete
                    </span>
                    <span>
                      <strong>
                        {workspace.phases
                          .filter((p) => p.status === "active")
                          .length.toString()
                          .padStart(2, "0")}
                      </strong>{" "}
                      in progress
                    </span>
                    <span>
                      <strong>
                        {workspace.phases
                          .filter((p) => p.status === "planned")
                          .length.toString()
                          .padStart(2, "0")}
                      </strong>{" "}
                      ahead
                    </span>
                    <p>Each phase earns the next.</p>
                  </div>
                  <div className="roadmap-layout">
                    <div className="phase-list">
                      {workspace.phases.map((p) => (
                        <button
                          key={p.id}
                          className={`phase-row ${phaseId === p.id ? "chosen" : ""}`}
                          aria-label={`Phase ${p.number}: ${p.title}, ${p.status === "active" ? "in progress" : p.status}`}
                          onClick={() => setPhaseId(p.id)}
                          aria-pressed={phaseId === p.id}
                        >
                          <span className="phase-number">{p.number}</span>
                          <span className="phase-row-title">
                            {p.title}
                            <Status value={p.status} />
                          </span>
                          <ChevronRight size={17} />
                        </button>
                      ))}
                    </div>
                    {selectedPhase && (
                      <section
                        className="panel phase-detail"
                        key={selectedPhase.id}
                      >
                        <span className="eyebrow">
                          RESEARCH PHASE {selectedPhase.number}
                        </span>
                        <div className="detail-number">
                          {selectedPhase.number}
                          <span> / TELESTO</span>
                        </div>
                        <Status value={selectedPhase.status} />
                        <h2>{selectedPhase.title}</h2>
                        <p>{selectedPhase.summary}</p>
                        <div className="exit-criterion">
                          <span className="eyebrow">
                            WHAT SUCCESS LOOKS LIKE
                          </span>
                          <p>{selectedPhase.exitCriterion}</p>
                        </div>
                        <ul className="milestone-list">
                          {selectedPhase.milestones.map((m) => (
                            <li key={m.label} className={m.status}>
                              {m.status === "complete" ? (
                                <Check size={15} />
                              ) : (
                                <CircleDot size={15} />
                              )}
                              <span>{m.label}</span>
                            </li>
                          ))}
                        </ul>
                        <div className="phase-results">
                          <span className="eyebrow">PUBLISHED RESULTS</span>
                          {workspace.runs.filter(
                            (r) => r.phaseId === selectedPhase.id,
                          ).length ? (
                            workspace.runs
                              .filter((r) => r.phaseId === selectedPhase.id)
                              .map((r) => (
                                <button
                                  key={r.id}
                                  className="panel-link"
                                  onClick={() => {
                                    setRunId(r.id);
                                    navigate("twin");
                                  }}
                                >
                                  {r.label} · seed {r.seed}
                                  <ArrowUpRight size={16} />
                                </button>
                              ))
                          ) : (
                            <p>No results published for this phase yet.</p>
                          )}
                        </div>
                      </section>
                    )}
                  </div>
                </>
              )}
              {view === "evidence" && (
                <>
                  <div className="evidence-intro">
                    <ShieldCheck size={24} />
                    <p>
                      Evidence before complexity.
                      <br />
                      <span>
                        Implementation status and limitations from the
                        repository.
                      </span>
                    </p>
                    <span className="tiny-tag">RESEARCH TESTBED</span>
                  </div>
                  <div className="evidence-grid">
                    {workspace.evidence.map((item) => (
                      <article className="panel evidence-card" key={item.title}>
                        <div className="evidence-card-top">
                          <span className={`evidence-icon ${item.status}`}>
                            {item.status === "verified" ? (
                              <CheckCheck size={20} />
                            ) : item.status === "pending" ? (
                              <CircleDot size={20} />
                            ) : (
                              <ShieldCheck size={20} />
                            )}
                          </span>
                          <span
                            className={`status ${item.status === "verified" ? "complete" : "planned"}`}
                          >
                            {item.status === "verified"
                              ? "Established"
                              : item.status === "pending"
                                ? "Open item"
                                : "Research boundary"}
                          </span>
                        </div>
                        <h2>{item.title}</h2>
                        <p>{item.detail}</p>
                        <div className="source-reference">
                          <BookOpen size={13} />
                          <code>{item.source}</code>
                        </div>
                      </article>
                    ))}
                  </div>
                </>
              )}
            </>
          )}
          <footer className="main-footer">
            <span>
              <span className="footer-mark">✳</span> TELESTO{" "}
              <span className="footer-divider">/</span> Learn the process.
            </span>
            <span>
              Simulation research <span className="footer-divider">·</span>{" "}
              Built with intention.
            </span>
          </footer>
        </main>
      </div>
      {settings && (
        <Settings
          endpoint={base ?? ""}
          onClose={() => setSettings(false)}
          onSave={changeEndpoint}
        />
      )}
      <div className={`toast ${toast ? "visible" : ""}`} role="status">
        {toast && (
          <>
            <Check size={16} />
            {toast}
          </>
        )}
      </div>
    </div>
  );
}

function Stat({
  label,
  icon: Icon,
  value,
  unit,
  detail,
}: {
  label: string;
  icon: LucideIcon;
  value: string;
  unit?: string;
  detail: string;
}) {
  return (
    <article className="stat">
      <div className="stat-label">
        <span>{label}</span>
        <Icon size={16} />
      </div>
      <div className="stat-value">
        {value}
        <span>{unit}</span>
      </div>
      <p>{detail}</p>
    </article>
  );
}

function Settings({
  endpoint,
  onClose,
  onSave,
}: {
  endpoint: string;
  onClose: () => void;
  onSave: (value: string) => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [value, setValue] = useState(
    endpoint || "http://127.0.0.1:8000/api/v1",
  );
  const [mode, setMode] = useState(endpoint ? "api" : "demo");
  const [message, setMessage] = useState("");
  useEffect(() => {
    const el = dialog.current!;
    const previous = document.activeElement as HTMLElement | null;
    el.showModal();
    return () => {
      el.close();
      previous?.focus();
    };
  }, []);
  return (
    <dialog
      ref={dialog}
      className="settings-dialog"
      aria-labelledby="connection-title"
      onCancel={onClose}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="dialog-inner">
        <div className="dialog-heading">
          <span className="eyebrow">WORKSPACE CONNECTION</span>
          <button
            className="icon-button"
            aria-label="Close settings"
            onClick={onClose}
          >
            <X size={18} />
          </button>
        </div>
        <h2 id="connection-title">Your research. Your source.</h2>
        <p>Choose the data behind the observatory.</p>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            try {
              if (mode === "api" && !value.trim())
                throw new Error("Enter an API URL.");
              onSave(mode === "demo" ? "" : normalizeEndpoint(value));
            } catch (err) {
              setMessage((err as Error).message);
            }
          }}
        >
          <label className={`source-option ${mode === "demo" ? "chosen" : ""}`}>
            <input
              type="radio"
              name="mode"
              value="demo"
              checked={mode === "demo"}
              onChange={() => {
                setMode("demo");
                setMessage("");
              }}
            />
            <div>
              <strong>Bundled simulation</strong>
              <span>Real seed-42 results. Works without a backend.</span>
            </div>
            <Database size={20} />
          </label>
          <label className={`source-option ${mode === "api" ? "chosen" : ""}`}>
            <input
              type="radio"
              name="mode"
              value="api"
              checked={mode === "api"}
              onChange={() => setMode("api")}
            />
            <div>
              <strong>Connect an API</strong>
              <span>Read results from your research environment.</span>
            </div>
            <Network size={20} />
          </label>
          {mode === "api" && (
            <label className="endpoint-label">
              API base URL
              <input
                type="url"
                required
                value={value}
                onChange={(e) => {
                  setValue(e.target.value);
                  setMessage("");
                }}
                placeholder="http://127.0.0.1:8000/api/v1"
              />
              <small>Read-only connection · schema version 1.0</small>
            </label>
          )}
          {message && (
            <p role="alert" className="form-error">
              {message}
            </p>
          )}
          <div className="dialog-actions">
            <button
              type="button"
              className="button secondary"
              onClick={onClose}
            >
              Cancel
            </button>
            <button type="submit" className="button primary">
              Apply connection <ArrowRight size={15} />
            </button>
          </div>
        </form>
      </div>
    </dialog>
  );
}
