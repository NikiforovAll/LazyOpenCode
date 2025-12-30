/**
 * Compaction Plugin - customizes context during session compaction.
 *
 * This plugin demonstrates using the 'experimental.session.compacting' hook
 * to inject additional context when a session is compacted.
 */
import type { Plugin } from "@opencode-ai/plugin"

export const CompactionPlugin: Plugin = async (ctx) => {
  return {
    "experimental.session.compacting": async (input, output) => {
      // Inject additional context into the compaction prompt
      output.context.push(`## Custom Context

Include any state that should persist across compaction:
- Current task status
- Important decisions made
- Files being actively worked on`)
    },
  }
}
