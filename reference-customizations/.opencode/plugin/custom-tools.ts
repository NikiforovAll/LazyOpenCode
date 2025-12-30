/**
 * Custom Tools Plugin - demonstrates adding custom tools via plugin.
 *
 * Plugins can define their own tools that OpenCode can call,
 * alongside the built-in tools.
 */
import { type Plugin, tool } from "@opencode-ai/plugin"

export const CustomToolsPlugin: Plugin = async (ctx) => {
  return {
    tool: {
      greet: tool({
        description: "Greets a user by name",
        args: {
          name: tool.schema.string(),
        },
        async execute(args, ctx) {
          return `Hello ${args.name}! Welcome to OpenCode.`
        },
      }),

      timestamp: tool({
        description: "Returns the current timestamp",
        args: {},
        async execute(args, ctx) {
          return new Date().toISOString()
        },
      }),
    },
  }
}
