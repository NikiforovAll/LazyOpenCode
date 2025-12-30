import { tool } from "@opencode-ai/plugin"

// Multiple exports create separate tools: math_add, math_multiply, math_divide

export const add = tool({
  description: "Add two numbers",
  args: {
    a: tool.schema.number().describe("First number"),
    b: tool.schema.number().describe("Second number"),
  },
  async execute(args) {
    return args.a + args.b
  },
})

export const multiply = tool({
  description: "Multiply two numbers",
  args: {
    a: tool.schema.number().describe("First number"),
    b: tool.schema.number().describe("Second number"),
  },
  async execute(args) {
    return args.a * args.b
  },
})

export const divide = tool({
  description: "Divide two numbers",
  args: {
    a: tool.schema.number().describe("Dividend"),
    b: tool.schema.number().describe("Divisor"),
  },
  async execute(args) {
    if (args.b === 0) {
      throw new Error("Cannot divide by zero")
    }
    return args.a / args.b
  },
})
