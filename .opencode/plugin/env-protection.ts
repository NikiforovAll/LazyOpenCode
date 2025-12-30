/**
 * Environment Protection Plugin - prevents reading .env files.
 *
 * This plugin demonstrates using the 'tool.execute.before' hook
 * to intercept and block certain tool operations.
 */
export const EnvProtection = async ({
  project,
  client,
  $,
  directory,
  worktree,
}) => {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool === "read" && output.args.filePath.includes(".env")) {
        throw new Error("Do not read .env files")
      }
    },
  }
}
