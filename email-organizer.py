#!/usr/bin/env python3
"""
Email Organization Script
Organizes Gmail emails based on classification rules
"""

import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

def classify_email(sender: str, subject: str, body_preview: str = "") -> Tuple[str, bool]:
    """
    Classify an email into one of the categories.
    Returns (category, should_delete)
    """
    sender_lower = sender.lower()
    subject_lower = subject.lower()
    body_lower = body_preview.lower()

    # Social Notifications (DELETE)
    social_keywords = [
        'facebook', 'instagram', 'twitter', 'reddit', 'discord',
        'tiktok', 'snapchat', '@twitter.com', '@instagram.com',
        'notifications-noreply@facebookmail.com'
    ]
    for keyword in social_keywords:
        if keyword in sender_lower or keyword in subject_lower:
            return "social_notifications", True

    # Security Alerts (ARCHIVE + TAG)
    security_keywords = [
        'suspicious sign-in', 'unusual activity', 'verify your identity',
        'confirm your identity', 'password change', 'new device',
        'security alert', 'suspicious activity', 'unauthorized access',
        'two-factor', '2fa', 'security key'
    ]
    for keyword in security_keywords:
        if keyword in subject_lower or keyword in body_lower:
            return "security_alerts", False

    # Important Emails (KEEP IN INBOX)
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
    for keyword in important_keywords:
        if keyword in subject_lower or keyword in body_lower:
            return "important", False

    # Confirmations (ARCHIVE + TAG)
    confirmation_keywords = [
        'confirmation', 'confirmed', 'verify', 'verification',
        'purchase confirmation', 'order confirmation', 'booking confirmed',
        'registration confirmed', 'survey response', 'receipt',
        'transaction', 'payment received', 'payment confirmed',
        'stock purchase', 'trade executed'
    ]
    for keyword in confirmation_keywords:
        if keyword in subject_lower or keyword in body_lower:
            return "confirmations", False

    # Marketing/Newsletters (ARCHIVE)
    marketing_keywords = [
        'unsubscribe', 'promotional', 'promotion', 'sale', 'discount',
        'limited time', 'offer', 'coupon', 'deal', 'shop now',
        'newsletter', 'marketing', 'exclusive', 'new arrival',
        'flash sale', 'special offer', '% off'
    ]
    for keyword in marketing_keywords:
        if keyword in subject_lower or keyword in body_lower:
            return "marketing", False

    # Default: Keep important (when uncertain)
    return "important", False


def process_emails(emails: List[Dict]) -> Dict:
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
            sender = email.get("from", "")
            subject = email.get("subject", "")
            body_preview = email.get("snippet", "")

            category, should_delete = classify_email(sender, subject, body_preview)

            email_info = {
                "id": email.get("id"),
                "from": sender,
                "subject": subject,
                "date": email.get("internalDate")
            }

            results["emails_by_category"][category].append(email_info)

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


def main():
    """Main entry point."""
    print("📧 Email Organization Routine")
    print("=" * 50)
    print(f"⏰ Running at: {datetime.now().isoformat()}")

    # For now, demonstrate the classification logic
    sample_emails = [
        {
            "id": "1",
            "from": "noreply@instagram.com",
            "subject": "Sarah liked your photo",
            "snippet": "Sarah has liked your recent photo",
            "internalDate": datetime.now().isoformat()
        },
        {
            "id": "2",
            "from": "amazon@amazon.com",
            "subject": "Your order has shipped - Tracking number included",
            "snippet": "Your package is on the way",
            "internalDate": datetime.now().isoformat()
        },
        {
            "id": "3",
            "from": "security@google.com",
            "subject": "Unusual activity detected on your Google account",
            "snippet": "We detected unusual activity",
            "internalDate": datetime.now().isoformat()
        },
        {
            "id": "4",
            "from": "deals@store.com",
            "subject": "Flash Sale - 50% off everything",
            "snippet": "Limited time offer",
            "internalDate": datetime.now().isoformat()
        }
    ]

    results = process_emails(sample_emails)

    print("\n📊 Processing Results:")
    print("=" * 50)
    print(f"Total emails processed: {results['total_processed']}")
    print(f"✅ Important (kept): {results['important_kept']}")
    print(f"📋 Confirmations (archived): {results['confirmations_archived']}")
    print(f"🔒 Security Alerts (archived): {results['security_alerts_archived']}")
    print(f"🗑️  Social Notifications (deleted): {results['social_notifications_deleted']}")
    print(f"📢 Marketing (archived): {results['marketing_archived']}")

    if results['errors']:
        print(f"\n⚠️  Errors: {len(results['errors'])}")
        for error in results['errors']:
            print(f"  - {error['email']}: {error['error']}")

    # Save results to file
    log_file = "routine_logs.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(results) + "\n")

    print(f"\n✅ Results logged to {log_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
