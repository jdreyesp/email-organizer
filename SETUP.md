# Email Organizer Setup Guide

This project provides automated email organization for Gmail based on intelligent classification.

## Overview

The email organizer classifies emails into the following categories:

- **Important** (Keep in Inbox): Orders, job opportunities, bills, travel alerts, event tickets, password resets
- **Confirmations** (Archive + Tag): Account verifications, receipts, survey confirmations, payment confirmations
- **Security Alerts** (Archive + Tag): Suspicious activity, identity verification, password changes, new device alerts
- **Social Notifications** (Delete): Facebook, Instagram, Twitter, Reddit, Discord, TikTok, Snapchat
- **Marketing** (Archive): Promotional emails, newsletters, sales, coupons, unsubscribe links

## Available Scripts

### 1. `email-organizer.py` (No Gmail Integration)

Standalone email classifier that demonstrates the classification logic without requiring Gmail API credentials.

```bash
python3 email-organizer.py
```

**Features:**
- Tests classification logic with sample emails
- No external dependencies or authentication required
- Logs results to `routine_logs.jsonl`

### 2. `gmail-organizer.py` (Full Gmail Integration)

Complete Gmail email organizer with OAuth2 authentication and automatic email management.

```bash
python3 gmail-organizer.py
```

**Features:**
- Fetches unread emails from the last 24 hours
- Automatically classifies each email
- Archives, deletes, or tags emails based on category
- Creates required labels if they don't exist
- Marks emails as read after processing
- Detailed logging of all actions

## Gmail API Setup

To use the full Gmail integration:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project and enable Gmail API
3. Create OAuth2 credentials (Desktop application type)
4. Download credentials as JSON and save as `credentials.json` in this directory
5. Install required libraries:
   ```bash
   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```
6. Run: `python3 gmail-organizer.py`
7. First run will open a browser for authentication

## Scheduling

### Linux/macOS (crontab)
```bash
0 9 * * * cd /path/to/email-organizer && python3 gmail-organizer.py
```

Run daily at 9 AM.

### Windows (Task Scheduler)
Create a task to run `python3 gmail-organizer.py` at desired intervals.

## Classification Rules

Emails are classified by keyword matching in sender, subject, and body:

- **Important**: Orders, shipping, jobs, bills, travel, events, password resets
- **Confirmations**: Verifications, receipts, bookings, payments, transactions
- **Security Alerts**: Suspicious activity, identity checks, password changes, new devices
- **Social**: Facebook, Instagram, Twitter, Reddit, Discord, TikTok, Snapchat notifications
- **Marketing**: Unsubscribe links, promotions, sales, newsletters, coupons, deals

## Output and Logging

Results are logged to `routine_logs.jsonl` in JSON Lines format with:
- Total emails processed
- Count by category
- List of emails in each category
- Any errors encountered
- Timestamp

View recent logs:
```bash
tail -5 routine_logs.jsonl | jq .
```

## Troubleshooting

**ModuleNotFoundError: No module named 'google'**
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

**Gmail API authentication fails**
- Verify `credentials.json` exists in the project directory
- Delete `token.json` to re-authenticate
- Check Gmail API is enabled in Google Cloud Console
- Ensure OAuth2 credentials are for "Desktop application"

**Permission denied for labels/archive**
- Verify OAuth2 credentials have `gmail.modify` scope
- Regenerate credentials if needed

## Privacy & Security

- **Never commit** `credentials.json` or `token.json` to version control
- **Logs contain** email subjects and senders - keep them secure
- **Deleted emails** go to Gmail Trash (30-day retention) before permanent deletion
- **Scopes used**: `gmail.modify` (read and modify emails)

## Node.js Alternative

Original `email-organizer-routine.js` requires ANTHROPIC_API_KEY:
```bash
ANTHROPIC_API_KEY=your-key npm start
```

## Support

- Gmail API docs: https://developers.google.com/gmail/api
- Google Auth library: https://github.com/googleapis/google-auth-library-python
- Classification logic: See `EmailClassifier` class in `gmail-organizer.py`
