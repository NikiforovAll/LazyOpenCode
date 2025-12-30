import { tool } from "@opencode-ai/plugin"

// Example: Tool that invokes a Python script
// The tool definition is TypeScript, but execution can use any language

export default tool({
  description: "Run a Python script with arguments",
  args: {
    script: tool.schema.string().describe("Path to Python script"),
    args: tool.schema.array(tool.schema.string()).describe("Arguments to pass"),
  },
  async execute(args) {
    const scriptArgs = args.args.join(" ")
    const result = await Bun.$`python3 ${args.script} ${scriptArgs}`.text()
    return result.trim()
  },
})
