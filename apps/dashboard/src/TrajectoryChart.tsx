import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { Channel, Run } from "./data";

export default function TrajectoryChart({
  run,
  channel,
  cursor,
}: {
  run: Run;
  channel: Channel;
  cursor: number;
}) {
  // Keep the chart light while always retaining the final sample. CSV retains every row.
  const stride = Math.max(1, Math.ceil(run.samples.length / 400));
  const points = run.samples.filter(
    (_, i) => i % stride === 0 || i === run.samples.length - 1,
  );
  return (
    <div
      className="chart"
      role="img"
      aria-label={`${channel.label} trajectory in ${channel.unit}, from ${run.samples[0].time} to ${run.samples.at(-1)!.time} hours. Current value ${run.samples[cursor][channel.key].toFixed(3)}. Full data available through Export CSV.`}
    >
      <ResponsiveContainer width="100%" height="100%" minWidth={0}>
        <AreaChart
          data={points}
          margin={{ top: 12, right: 12, bottom: 0, left: -20 }}
          accessibilityLayer
        >
          <defs>
            <linearGradient id="trajectory-fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--accent)" stopOpacity={0.2} />
              <stop offset="100%" stopColor="var(--accent)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid
            stroke="var(--line)"
            vertical={false}
            strokeDasharray="3 5"
          />
          <XAxis
            dataKey="time"
            type="number"
            domain={["dataMin", "dataMax"]}
            tickLine={false}
            axisLine={false}
            tick={{ fill: "var(--muted)", fontSize: 11 }}
            tickFormatter={(n) => `${Math.round(n)} h`}
            minTickGap={35}
          />
          <YAxis
            tickLine={false}
            axisLine={false}
            tick={{ fill: "var(--muted)", fontSize: 11 }}
            domain={["auto", "auto"]}
            tickFormatter={(n) =>
              Number(n).toLocaleString("en", {
                maximumFractionDigits: 1,
                notation: Math.abs(n) >= 10000 ? "compact" : "standard",
              })
            }
          />
          <Tooltip
            contentStyle={{
              background: "var(--surface)",
              border: "1px solid var(--line)",
              borderRadius: 10,
              color: "var(--text)",
              fontSize: 12,
            }}
            labelFormatter={(n) => `${Number(n).toFixed(1)} simulated hours`}
            formatter={(value) => [
              `${Number(value).toFixed(3)} ${channel.unit}`,
              channel.label,
            ]}
          />
          <Area
            dataKey={channel.key}
            type="linear"
            stroke="var(--accent)"
            fill="url(#trajectory-fill)"
            strokeWidth={2}
            isAnimationActive={false}
          />
          <ReferenceLine
            x={run.samples[cursor].time}
            stroke="var(--text)"
            strokeDasharray="4 4"
            strokeOpacity={0.4}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
