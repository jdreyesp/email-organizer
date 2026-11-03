#!/usr/bin/env python3
"""
Gmail Email Organization Script
Connects to Gmail API and organizes emails based on classification rules
"""

import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import base64
from pathlib import Path

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.api_core.exceptions import GoogleAPICallError
    from googleapiclient.discovery import build
    GMAIL_API_AVAILABLE = True
except ImportError:
    GMAIL_API_AVAILABLE = False

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


class EmailClassifier:
    """Classifies emails based on predefined rules."""

    def classify(self, sender: str, subject: str, body_preview: str = "") -> Tuple[str, bool]:
        """
        Classify an email into one of the categories.
        Returns (category, should_delete)
        """
        sender_lower = sender.lower()
        subject_lower = subject.lower()
        body_lower = body_preview.lower()

        # Social Notifications (DELETE)
        if self._matches_social(sender_lower, subject_lower):
            return "social_notifications", True

        # Security Alerts (ARCHIVE + TAG)
        if self._matches_security(subject_lower, body_lower):
            return "security_alerts", False

        # Important Emails (KEEP IN INBOX)
        if self._matches_important(subject_lower, body_lower):
            return "important", False

        # Confirmations (ARCHIVE + TAG)
        if self._matches_confirmation(subject_lower, body_lower):
            return "confirmations", False

        # Marketing/Newsletters (ARCHIVE)
        if self._matches_marketing(subject_lower, body_lower):
            return "marketing", False

        # Default: Keep important (when uncertain)
        return "important", False

    @staticmethod
    def _matches_social(sender: str, subject: str) -> bool:
        social_keywords = [
            'facebook', 'instagram', 'twitter', 'reddit', 'discord',
            'tiktok', 'snapchat', '@twitter.com', '@instagram.com',
            'notifications-noreply@facebookmail.com'
        ]
        return any(keyword in sender or keyword in subject for keyword in social_keywords)

    @staticmethod
    def _matches_security(subject: str, body: str) -> bool:
        security_keywords = [
            'suspicious sign-in', 'unusual activity', 'verify your identity',
            'confirm your identity', 'password change', 'new device',
            'security alert', 'suspicious activity', 'unauthorized access',
            'two-factor', '2fa', 'security key'
        ]
        return any(keyword in subject or keyword in body for keyword in security_keywords)

    @staticmethod
    def _matches_important(subject: str, body: str) -> bool:
        important_keywords = [
            'order confirmation', 'shipping', 'tracking number', 'tracking update',
            'linkedin', 'recruiter', 'job opportunity', 'job posting',
            'game beta', 'beta invitation', 'event beta',
            'electricity bill', 'water bill', 'utility bill', 'billing',
            'travel advisory', 'flight alert', 'flight status', 'trip',
            'event tickets', 'booking confirmation', 'confirmation number',
            'password reset', 'verify your email', 'verify account',
            'service outage', 'service notification', 'maintenance',
            'urgent', 'action required', 'immediate action'
        ]
        return any(keyword in subject or keyword in body for keyword in important_keywords)

    @staticmethod
    def _matches_confirmation(subject: str, body: str) -> bool:
        confirmation_keywords = [
            'purchase confirmation', 'order confirmed', 'booking confirmed',
            'registration confirmed', 'survey response', 'receipt',
            'transaction received', 'payment received', 'payment confirmed',
            'stock purchase', 'trade executed', 'email verification',
            'account verification'
        ]
        return any(keyword in subject or keyword in body for keyword in confirmation_keywords)

    @staticmethod
    def _matches_marketing(subject: str, body: str) -> bool:
        marketing_keywords = [
            'unsubscribe', 'promotional', 'promotion', 'sale', 'discount',
            'limited time', 'offer', 'coupon', 'deal', 'shop now',
            'newsletter', 'marketing', 'exclusive', 'new arrival',
            'flash sale', 'special offer', '% off'
        ]
        return any(keyword in subject or keyword in body for keyword in marketing_keywords)


class GmailOrganizer:
    """Manages Gmail email organization."""

    def __init__(self, credentials_file: str = "credentials.json"):
        self.service = None
        self.classifier = EmailClassifier()
        self.credentials_file = credentials_file
        self.labels_cache = {}

    def authenticate(self) -> bool:
        """Authenticate with Gmail API."""
        if not GMAIL_API_AVAILABLE:
            print("❌ Gmail API libraries not available")
            return False

        token_file = "token.json"
        creds = None

        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            elif os.path.exists(self.credentials_file):
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            else:
                print(f"❌ {self.credentials_file} not found")
                return False

            with open(token_file, 'w') as token:
                token.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)
        return True

    def get_unread_emails_24h(self, max_results: int = 10) -> List[Dict]:
        """Get unread emails from the last 24 hours."""
        if not self.service:
            return []

        try:
            # Query for unread emails from last 24 hours
            query = 'is:unread newer_than:1d'
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            emails = []

            for msg in messages:
                email_data = self._get_message_details(msg['id'])
                if email_data:
                    emails.append(email_data)

            return emails

        except GoogleAPICallError as e:
            print(f"❌ Error fetching emails: {e}")
            return []

    def _get_message_details(self, message_id: str) -> Optional[Dict]:
        """Get details of a specific message."""
        try:
            msg = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '')

            # Get snippet/preview
            snippet = msg.get('snippet', '')

            return {
                'id': message_id,
                'subject': subject,
                'from': sender,
                'snippet': snippet
            }
        except Exception as e:
            print(f"⚠️  Error getting message {message_id}: {e}")
            return None

    def _ensure_label(self, label_name: str) -> Optional[str]:
        """Ensure a label exists, creating it if needed."""
        if label_name in self.labels_cache:
            return self.labels_cache[label_name]

        try:
            # List existing labels
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])

            for label in labels:
                if label['name'] == label_name:
                    self.labels_cache[label_name] = label['id']
                    return label['id']

            # Create label if it doesn't exist
            label_body = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            created_label = self.service.users().labels().create(
                userId='me',
                body=label_body
            ).execute()

            self.labels_cache[label_name] = created_label['id']
            return created_label['id']
        except Exception as e:
            print(f"⚠️  Error managing label {label_name}: {e}")
            return None

    def process_emails(self, emails: List[Dict]) -> Dict:
        """Process and classify emails."""
        results = {
            "total_processed": len(emails),
            "important_kept": 0,
            "confirmations_archived": 0,
            "security_alerts_archived": 0,
            "social_notifications_deleted": 0,
            "marketing_archived": 0,
            "emails_by_category": {
                "important": [],
                "confirmations": [],
                "security_alerts": [],
                "social_notifications": [],
                "marketing": []
            },
            "timestamp": datetime.now().isoformat(),
            "errors": []
        }

        for email in emails:
            try:
                category, should_delete = self.classifier.classify(
                    email['from'],
                    email['subject'],
                    email.get('snippet', '')
                )

                email_info = {
                    "subject": email['subject'],
                    "from": email['from']
                }

                results["emails_by_category"][category].append(email_info)

                # Apply actions if Gmail service is available
                if self.service:
                    self._apply_action(email['id'], category, should_delete)

                # Count by category
                if category == "important":
                    results["important_kept"] += 1
                elif category == "confirmations":
                    results["confirmations_archived"] += 1
                elif category == "security_alerts":
                    results["security_alerts_archived"] += 1
                elif category == "social_notifications":
                    results["social_notifications_deleted"] += 1
                elif category == "marketing":
                    results["marketing_archived"] += 1

            except Exception as e:
                results["errors"].append({
                    "email": email.get("subject", "Unknown"),
                    "error": str(e)
                })

        return results

    def _apply_action(self, message_id: str, category: str, should_delete: bool):
        """Apply action to a message."""
        try:
            if should_delete:
                # Delete social notifications
                self.service.users().messages().delete(
                    userId='me',
                    id=message_id
                ).execute()
            else:
                # Archive and apply label for other categories
                self.service.users().messages().modify(
                    userId='me',
                    id=message_id,
                    body={'removeLabelIds': ['INBOX']}
                ).execute()

                if category != "important":
                    label_name = category.replace('_', ' ').title()
                    label_id = self._ensure_label(label_name)
                    if label_id:
                        self.service.users().messages().modify(
                            userId='me',
                            id=message_id,
                            body={'addLabelIds': [label_id]}
                        ).execute()

                # Mark as read
                self.service.users().messages().modify(
                    userId='me',
                    id=message_id,
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
        except Exception as e:
            print(f"⚠️  Error applying action to {message_id}: {e}")


def main():
    """Main entry point."""
    print("📧 Gmail Email Organization Routine")
    print("=" * 60)
    print(f"⏰ Running at: {datetime.now().isoformat()}")
    print()

    organizer = GmailOrganizer()

    # Try to authenticate
    print("🔐 Attempting Gmail authentication...")
    if not organizer.authenticate():
        print("\n⚠️  Gmail API authentication failed")
        print("To set up Gmail access:")
        print("1. Create OAuth2 credentials at: https://console.cloud.google.com")
        print("2. Download credentials as credentials.json in this directory")
        print("3. Run this script again")
        return 1

    print("✅ Authenticated with Gmail\n")

    # Get unread emails from last 24 hours
    print("📬 Fetching unread emails from last 24 hours...")
    emails = organizer.get_unread_emails_24h(max_results=20)

    if not emails:
        print("No unread emails found in the last 24 hours")
        return 0

    print(f"Found {len(emails)} unread email(s)\n")

    # Process emails
    print("🔄 Processing and classifying emails...")
    results = organizer.process_emails(emails)

    # Display results
    print("\n📊 Processing Results:")
    print("=" * 60)
    print(f"Total processed:           {results['total_processed']}")
    print(f"✅ Important (kept):        {results['important_kept']}")
    print(f"📋 Confirmations (archived): {results['confirmations_archived']}")
    print(f"🔒 Security Alerts (archived): {results['security_alerts_archived']}")
    print(f"🗑️  Social Notifications (deleted): {results['social_notifications_deleted']}")
    print(f"📢 Marketing (archived):    {results['marketing_archived']}")

    # Show breakdown
    print("\n📋 Email Breakdown by Category:")
    for category, emails_in_cat in results['emails_by_category'].items():
        if emails_in_cat:
            print(f"\n{category.replace('_', ' ').title()}:")
            for email in emails_in_cat[:3]:  # Show first 3
                print(f"  • {email['subject'][:50]}")
                print(f"    From: {email['from'][:50]}")
            if len(emails_in_cat) > 3:
                print(f"  ... and {len(emails_in_cat) - 3} more")

    if results['errors']:
        print(f"\n⚠️  Errors encountered: {len(results['errors'])}")
        for error in results['errors'][:3]:
            print(f"  • {error['email']}: {error['error']}")

    # Log results
    log_file = "routine_logs.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(results) + "\n")

    print(f"\n✅ Results logged to {log_file}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
