import { tool } from "opencode";

export default tool({
  name: "search",
  description: "Search for files matching a pattern",
  parameters: {
    pattern: {
      type: "string",
      description: "The glob pattern to search for",
    },
  },
  execute: async ({ pattern }) => {
    // Implementation would go here
    return `Found files matching: ${pattern}`;
  },
});
