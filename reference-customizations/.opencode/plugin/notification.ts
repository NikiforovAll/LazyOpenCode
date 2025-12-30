/**
 * Notification Plugin - sends system notifications on session events.
 *
 * This plugin demonstrates using the 'event' handler to respond
 * to OpenCode events like session.idle.
 */
export const NotificationPlugin = async ({
  project,
  client,
  $,
  directory,
  worktree,
}) => {
  console.log("NotificationPlugin initialized!")

  return {
    event: async ({ event }) => {
      // Send notification on session completion
      if (event.type === "session.idle") {
        await $`osascript -e 'display notification "Session completed!" with title "opencode"'`
      }
    },
  }
}
