import { plugin } from "opencode";

export const MetricsPlugin = plugin({
  name: "metrics",
  hooks: {
    "session.start": async ({ session }) => {
      console.log(`Session started: ${session.id}`);
    },
    "session.end": async ({ session }) => {
      console.log(`Session ended: ${session.id}`);
    },
    "tool.execute.after": async ({ tool, result }) => {
      console.log(`Tool ${tool.name} executed`);
    },
  },
});

export default MetricsPlugin;
