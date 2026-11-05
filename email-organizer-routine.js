#!/usr/bin/env node

/**
 * Email Organization Routine
 * Runs daily on Anthropic's cloud infrastructure
 * Connects to Gmail via MCP and intelligently organizes emails
 *
 * NOTE: This routine is designed to run as a Claude Code Session.
 * It will be executed by Claude with access to Gmail MCP connector.
 */

import * as fs from "fs";

async function runEmailOrganization() {
  console.log("🚀 Starting Email Organization Routine...");
  console.log(`⏰ Timestamp: ${new Date().toISOString()}`);

  try {
    // Read CLAUDE.md for reference
    const claudeMd = fs.readFileSync("./CLAUDE.md", "utf-8");

    console.log("\n📋 Routine Instructions:");
    console.log("=".repeat(50));
    console.log(claudeMd);

    console.log("\n📧 Email Organization Task:");
    console.log("=".repeat(50));
    console.log(`
This routine should be executed by Claude with Gmail MCP connector enabled.

If running interactively in Claude Code:
1. Claude will use the Gmail MCP tool to fetch unread emails from last 24 hours
2. Emails will be classified according to the rules in CLAUDE.md
3. Required labels will be created: "Confirmations", "Security Alerts"
4. Appropriate actions will be taken:
   - Important emails: kept in inbox (unread)
   - Confirmations: archived with "Confirmations" label
   - Security alerts: archived with "Security Alerts" label
   - Social notifications: deleted
   - Marketing/newsletters: archived (no label)
5. All processed emails will be marked as read
6. Summary statistics will be reported

STATUS: Ready to process emails when Gmail MCP is connected.
`);

    // Log that routine is ready
    logToFile({
      timestamp: new Date().toISOString(),
      status: "ready",
      message: "Routine ready - waiting for Gmail MCP connector",
    });

    console.log("✅ Routine initialized and ready");
    console.log("📝 Awaiting Gmail MCP connector activation...");
  } catch (error) {
    console.error("❌ Error during routine initialization:", error);

    logToFile({
      timestamp: new Date().toISOString(),
      status: "error",
      error: error.message,
    });

    process.exit(1);
  }
}

function logToFile(data) {
  const logFile = "./routine_logs.jsonl";
  fs.appendFileSync(logFile, JSON.stringify(data) + "\n");
}

// Run the routine
runEmailOrganization();
