#!/usr/bin/env node

/**
 * Email Organization Routine
 * Runs daily on Anthropic's cloud infrastructure
 * Connects to Gmail via MCP and intelligently organizes emails
 */

import Anthropic from "@anthropic-ai/sdk";
import * as fs from "fs";

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

async function runEmailOrganization() {
  console.log("🚀 Starting Email Organization Routine...");
  console.log(`⏰ Timestamp: ${new Date().toISOString()}`);

  try {
    // Read CLAUDE.md for system context
    const claudeMd = fs.readFileSync("./CLAUDE.md", "utf-8");

    // Create the prompt that Claude will execute
    const prompt = `You are an email organization agent. Here are your instructions:

${claudeMd}

## Current Task
Run your email organization process now:
1. Use the Gmail MCP tool to fetch all unread emails from the last 24 hours
2. Classify and organize each email according to the rules above
3. Create the required labels if they don't exist
4. Apply the appropriate actions (keep in inbox, archive + tag, delete)
5. Mark emails as read after processing
6. Report back with detailed statistics

Start by connecting to Gmail and fetching the emails. Process them one by one, making decisions based on the classification rules. Be thorough and consistent.`;

    // Call Claude with the email organization task
    const response = await client.messages.create({
      model: "claude-opus-4-6",
      max_tokens: 4000,
      thinking: {
        type: "enabled",
        budget_tokens: 2000,
      },
      messages: [
        {
          role: "user",
          content: prompt,
        },
      ],
      tools: [
        {
          type: "bash",
          name: "bash",
        },
      ],
    });

    // Process the response
    console.log("\n📊 Processing Results:");
    console.log("=".repeat(50));

    for (const block of response.content) {
      if (block.type === "text") {
        console.log(block.text);
      } else if (block.type === "thinking") {
        console.log("\n💭 Claude's reasoning:", block.thinking.substring(0, 200) + "...");
      }
    }

    console.log("\n✅ Email Organization Routine Complete");
    console.log(`📝 Stop reason: ${response.stop_reason}`);

    // Log completion
    logToFile({
      timestamp: new Date().toISOString(),
      status: "completed",
      stopReason: response.stop_reason,
      summary: "Email organization completed successfully",
    });
  } catch (error) {
    console.error("❌ Error during email organization:", error);

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
