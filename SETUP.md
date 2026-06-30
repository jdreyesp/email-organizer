# Email Organizer Routine - Setup Guide

## Overview
This is a **Claude Code Routine** that runs on Anthropic's cloud infrastructure. Your computer doesn't need to be on. The automation runs daily at 9 AM (your timezone) automatically.

---

## Prerequisites
- ✅ Gmail account with MCP connector enabled (you already have this)
- ✅ Claude Pro or Claude Teams plan (required for Routines)
- ✅ Github account (optional, for storing the code)

---

## Setup Steps

### **Step 1: Prepare Your Local Repo (or just the files)**

You can either:
- **Option A:** Create a GitHub repo with these files
- **Option B:** Keep files locally and upload when creating the routine

Files you need:
```
.
├── CLAUDE.md                    (Agent instructions)
├── email-organizer-routine.js   (Main script)
├── package.json                 (Dependencies)
└── .env                         (Your API key, see below)
```

### **Step 2: Set Up Environment Variables**

The routine needs your Gmail MCP access. Add to `.env`:
```bash
ANTHROPIC_API_KEY=your-api-key-here
GMAIL_MCP_ENABLED=true
```

**Note:** If using GitHub, use Routine secrets instead (not .env):
- Go to your routine settings
- Add secret: `ANTHROPIC_API_KEY`
- Add secret: `GMAIL_MCP_ENABLED=true`

### **Step 3: Create the Routine via Claude.ai**

1. Go to **claude.ai** → click your profile → **Settings**
2. Find **"Scheduled Tasks"** or **"Routines"** section
3. Click **"+ New Routine"** or **"Create Routine"**
4. Fill in:
   - **Name:** "Email Organizer"
   - **Schedule:** Daily at 9:00 AM
   - **Timezone:** Your local timezone
   - **Repository/Files:** Upload or link your GitHub repo
   - **Command:** `npm install && npm start`
   - **Connectors:** Enable **Gmail MCP**
   - **API Key:** Paste your ANTHROPIC_API_KEY (or use Routine secrets)

5. Click **"Create"** or **"Deploy"**

### **Step 4: First Test Run**

Before waiting for the scheduled run:

1. In your routine settings, find the **"Run Now"** button
2. Click it to test immediately
3. Check the **Execution Logs** for output
4. Look for:
   - ✅ "Connecting to Gmail..."
   - ✅ "Processing X emails..."
   - ✅ "Created labels: Confirmations, Security Alerts"
   - ✅ "Email organization completed successfully"

### **Step 5: Monitor & Adjust**

After the first few automated runs:
- Review your inbox—important emails should stay
- Check archived emails with the "Confirmations" label
- Verify deleted emails were actually noise
- Adjust rules in **CLAUDE.md** if needed

---

## Customizing the Rules

Edit **CLAUDE.md** to:
- Add more email senders you care about
- Add keywords for specific categories
- Change label names
- Adjust what gets deleted vs archived

Example: To keep all emails from "boss@company.com" in inbox:
```markdown
## Important Emails (STAY IN INBOX)
- Emails from boss@company.com
- [rest of rules...]
```

After editing, push changes to GitHub and re-run the routine. The Routine will use the updated CLAUDE.md automatically.

---

## What the Routine Does Each Day

At 9 AM (your timezone):
1. ✅ Connects to your Gmail via the Gmail MCP connector
2. ✅ Fetches all unread emails from the last 24 hours
3. ✅ Claude reads and classifies each email using the rules
4. ✅ Creates labels if they don't exist: "Confirmations", "Security Alerts"
5. ✅ Archives + tags confirmations
6. ✅ Deletes social notifications
7. ✅ Archives marketing emails
8. ✅ Leaves important emails in inbox
9. ✅ Marks everything as read
10. ✅ Sends you a summary of what it did

---

## Costs

- **Routine execution:** ~$0.01 - $0.05 per daily run depending on email volume
- **API calls:** Minimal (only when routine fires)
- **No cost** when routine isn't running

---

## Troubleshooting

### "Gmail MCP not connected"
- Go to claude.ai Settings → Connectors
- Find Gmail → Click "Connect"
- Authorize access
- Retry the routine

### "Labels not found"
- Routine creates them automatically on first run
- If not, the routine creates them next execution
- Check Gmail → Settings → Labels to verify

### "Emails not being organized"
- Check routine execution logs for errors
- Verify Gmail MCP is enabled in routine settings
- Try a manual "Run Now" test first

### "Too many emails deleted"
- Review CLAUDE.md rules
- Add senders you want to keep to the "Important" section
- Re-run with updated rules

---

## Next Steps

Once you're confident in the automation:
1. **Expand:** Add more categories or rules
2. **Integrate:** Add Slack notifications when important emails arrive
3. **Combine:** Pair with Gmail filters for even smarter organization

---

## Support

For issues, check:
- Routine execution logs in Claude.ai Settings
- Gmail MCP connector status
- API key validity
- Ensure pro/Teams plan is active
