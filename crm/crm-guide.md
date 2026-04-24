# CRM System Guide
## Houston Bros Hospitality

---

## What is the CRM?

The **Customer Relationship Management (CRM)** system is the single source of truth for all guest and client relationships at Houston Bros. Every interaction — from the first inquiry to post-stay follow-up — is logged here to ensure consistent, personalized service and drive repeat business.

**Primary CRM Tool Recommendation:** HubSpot (Free tier available), or alternatives: Salesforce, Zoho CRM, or Airtable.

---

## CRM Data Structure

Every contact record must include:

### Contact Fields
| Field                   | Required? | Notes                                  |
|-------------------------|-----------|----------------------------------------|
| First Name              | ✅        |                                        |
| Last Name               | ✅        |                                        |
| Email Address           | ✅        | Primary contact method                 |
| Phone Number            | ✅        |                                        |
| Company / Organization  | If B2B    | Corporate clients                      |
| Contact Type            | ✅        | Individual / Corporate / Event Planner |
| Source                  | ✅        | Website / Referral / Social / Walk-in  |
| VIP Status              | ✅        | Standard / Silver / Gold / VIP         |
| Notes / Preferences     | ✅        | Food allergies, room preferences, etc. |
| Birthday / Anniversary  | If known  | For personalized outreach              |
| Assigned Rep            | ✅        | Who owns this relationship             |

### Booking / Deal Fields
| Field                   | Required? |
|-------------------------|-----------|
| Booking Type            | ✅        |
| Event/Stay Date         | ✅        |
| Guest Count             | ✅        |
| Package Selected        | ✅        |
| Total Value             | ✅        |
| Deposit Paid            | ✅        |
| Balance Due Date        | ✅        |
| Special Requests        | If any    |
| Status                  | ✅        |

---

## Lead & Deal Stages (Pipeline)

```
New Lead → Contacted → Qualified → Proposal Sent → Negotiation → Closed Won / Closed Lost
```

| Stage           | Definition                                        | Next Action                          |
|-----------------|---------------------------------------------------|--------------------------------------|
| New Lead        | Inquiry received, not yet contacted               | Contact within 1 hour                |
| Contacted       | First outreach made, awaiting response            | Follow up in 24 hours                |
| Qualified       | Needs confirmed, budget and dates known           | Send proposal within 24 hours        |
| Proposal Sent   | Proposal sent, awaiting decision                  | Follow up by phone in 48 hours       |
| Negotiation     | Active back-and-forth on terms                    | Resolve and close within 5 days      |
| Closed Won      | Contract signed, deposit received                 | Brief operations team; set reminders |
| Closed Lost     | Guest chose elsewhere or withdrew                 | Log reason; add to nurture campaign  |

---

## CRM Workflows & Automations

### 1. New Lead Notification
- Trigger: New form submission or lead entry
- Action: Notify assigned sales rep by email + task to respond within 1 hour

### 2. Proposal Follow-Up
- Trigger: Proposal Sent stage + 48 hours with no response
- Action: Auto-send follow-up email; create task for rep to call

### 3. Post-Stay Follow-Up
- Trigger: Check-out date + 24 hours
- Action: Send thank-you email with Google Review request + loyalty offer

### 4. Birthday / Anniversary Greetings
- Trigger: Birthday or anniversary date
- Action: Send personalized message with special offer

### 5. Re-Engagement Campaign
- Trigger: No activity from guest for 6 months
- Action: Add to "Win-Back" email sequence (3 emails over 4 weeks)

### 6. VIP Identification
- Trigger: 3+ bookings OR total spend > $3,000
- Action: Upgrade to VIP status; notify DOO; add to VIP list

---

## CRM Hygiene Rules

1. **Log every interaction** — calls, emails, meetings, on-site visits — within 24 hours.
2. **Update stage** immediately when a deal progresses or is lost.
3. **No duplicate contacts** — always search before creating a new record.
4. **Every active deal must have a next action** with a due date.
5. **Closed Lost deals require a reason** — this data improves future performance.
6. **Weekly CRM audit** by Sales Manager (Fridays): Check for overdue tasks, stale deals, missing data.
7. **Monthly data review** by DOO: Ensure ≥ 95% record completeness.

---

## Guest Communication Templates

### Initial Response Email
```
Subject: Thanks for reaching out to Houston Bros!

Hi [Name],

Thank you for contacting Houston Bros — we're excited to connect with you!

I'd love to learn more about [event/stay type] and see how we can make it perfect.

Could we schedule a quick 15-minute call this week? I'm available [offer 2–3 time slots].

Looking forward to hearing from you!

Warm regards,
[Your Name]
Houston Bros | [Phone] | [Email]
```

### Post-Stay Thank You Email
```
Subject: It was a pleasure hosting you, [Name]!

Hi [Name],

On behalf of the entire Houston Bros team — thank you for staying with us. It was truly a pleasure!

We hope everything was just as you imagined. If there's anything we can improve, please let us know directly at [email].

If you enjoyed your stay, we'd love a quick review on Google — it means the world to us: [Google Review Link]

As a thank-you, here's 10% off your next booking: [CODE]

We hope to see you again soon!

Warm regards,
[Your Name]
Houston Bros
```

### Booking Confirmation Email
```
Subject: Your Houston Bros booking is confirmed! 🎉

Hi [Name],

Great news — your booking is confirmed! Here are your details:

📅 Date: [Date]
🏠 Package: [Package Name]
👥 Guests: [Number]
💳 Deposit Paid: [Amount]
💰 Balance Due: [Amount] by [Date]

We'll be in touch 72 hours before your arrival with everything you need.

Can't wait to host you!

[Your Name]
Houston Bros
```

---

## Reporting & Analytics

Review these CRM reports weekly/monthly:

| Report                         | Frequency | Owner         |
|--------------------------------|-----------|---------------|
| Open Leads by Stage            | Weekly    | Sales Manager |
| Deals Won/Lost (with reason)   | Weekly    | Sales Manager |
| Revenue Forecast               | Weekly    | Sales Manager |
| Top Lead Sources               | Monthly   | Marketing Mgr |
| Average Deal Cycle Time        | Monthly   | DOO           |
| Guest Lifetime Value (LTV)     | Monthly   | DOO           |
| VIP Guest List                 | Monthly   | DOO           |
| Re-engagement Campaign Results | Monthly   | Marketing Mgr |
