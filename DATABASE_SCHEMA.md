# Database Schema Documentation

This document describes the complete database schema for the Valueloads AI Backend - a ConversAI Labs-style voice AI agent platform.

## Overview

**Total Tables:** 21 across 8 Django apps
**Database:** PostgreSQL
**Architecture:** Multi-tenant SaaS with company isolation

---

## Apps & Tables

### 📁 `apps/accounts` (4 tables)
- `Company` - Multi-tenant organizations
- `Employee` - User accounts (custom auth model)
- `APIKey` - API authentication tokens
- `AuditLog` - Compliance and security audit trail

### 📁 `apps/campaigns` (2 tables)
- `Campaign` - Marketing/sales campaigns
- `CampaignDailyStats` - Pre-aggregated analytics

### 📁 `apps/agents` (3 tables)
- `VoiceConfiguration` - Reusable voice settings
- `Agent` - AI voice agent configurations
- `AgentVersion` - Agent version snapshots for A/B testing

### 📁 `apps/leads` (3 tables)
- `Lead` - Contacts to be called
- `LeadImportBatch` - Bulk CSV import tracking
- `LeadNote` - Manual notes on leads

### 📁 `apps/calls` (4 tables)
- `Call` - Call interaction records
- `AIAnalysis` - AI sentiment/analysis results
- `CallRecording` - Recording metadata & storage
- `CallCost` - Detailed cost breakdown

### 📁 `apps/webhooks` (2 tables)
- `WebhookConfig` - Company webhook settings
- `WebhookDelivery` - Delivery attempts log

### 📁 `apps/integrations` (2 tables)
- `Integration` - Third-party CRM connections
- `IntegrationLog` - Sync activity logs

### 📁 `apps/exports` (1 table)
- `DataExport` - Large file export jobs

---

## Entity Relationship Diagram

```
COMPANY (Tenant Root)
  ├─→ Employee (many)
  ├─→ APIKey (many)
  ├─→ Campaign (many)
  │     ├─→ CampaignDailyStats (many)
  │     └─→ Agent (many)
  │           ├─→ Lead (many)
  │           │     ├─→ LeadNote (many)
  │           │     └─→ Call (many)
  │           ├─→ AgentVersion (many)
  │           └─→ Call (many)
  ├─→ Lead (many)
  ├─→ Call (many)
  │     ├─→ AIAnalysis (1:1)
  │     ├─→ CallRecording (1:1)
  │     ├─→ CallCost (1:1)
  │     └─→ WebhookDelivery (many)
  ├─→ WebhookConfig (1:1)
  ├─→ Integration (many)
  │     └─→ IntegrationLog (many)
  ├─→ DataExport (many)
  └─→ AuditLog (many)
```

---

## Core Models Detail

### Company
**Purpose:** Multi-tenant organization root
**Key Fields:**
- `plan_tier` - Subscription level (free, starter, pro, enterprise)
- `call_credits_remaining` - Usage quota
- `max_concurrent_calls` - Rate limit
- `timezone` - Default timezone for operations

**Indexes:**
- `(is_active, created_at)`

---

### Campaign
**Purpose:** Groups agents and tracks campaign performance
**Key Fields:**
- `status` - draft | active | paused | completed
- `call_type` - inbound | outbound
- `sale_cycle` - prospecting | qualification | proposal | negotiation | closed_won | closed_lost
- `allowed_calling_hours` - JSON with time restrictions per day
- `total_budget_usd` - Campaign spending limit

**Relationships:**
- 1 Campaign → Many Agents
- 1 Campaign → Many Leads

**Indexes:**
- `(company_id, status, created_at)`
- `(is_active, deleted_at)` - for soft deletes

---

### Agent
**Purpose:** AI voice agent configuration
**Key Fields:**
- `prompt` - System instructions for AI
- `welcome_message` - Opening greeting
- `max_attempts` - Call retry limit per lead
- `retry_delay_minutes` - Time between retries
- `model_name` - AI model (gpt-4-turbo, etc.)
- `temperature` - AI creativity (0-1)
- `enable_human_handoff` - Transfer to human option

**Relationships:**
- 1 Agent → Many Leads
- 1 Agent → Many Calls
- 1 Agent → 1 VoiceConfiguration
- 1 Agent → Many AgentVersions

**Indexes:**
- `(company_id, status)`
- `(campaign_id, status)`

---

### Lead
**Purpose:** Contact to be called
**Key Fields:**
- `phone_e164` - Phone in E.164 format (+14155552671)
- `status` - new | scheduled | in_progress | done | stopped
- `disposition` - not_interested | hung_up | completed | no_answer | callback_requested
- `attempts_count` - Number of call attempts
- `currently_in_call` - Lock to prevent concurrent calls
- `schedule_at` - Planned call time
- `custom_fields` - JSON for flexible metadata
- `tags` - JSON array for segmentation

**Important:**
- One lead per campaign (same person can exist in multiple campaigns as different lead records)
- E.164 phone format enforced

**Indexes:**
- `(company_id, status, created_at)`
- `(agent_id, status)`
- `(phone_e164, company_id)` - for duplicate checking
- `(status, schedule_at)` - for scheduler queries
- `(currently_in_call)` - for locking

---

### Call
**Purpose:** Record of each call interaction
**Key Fields:**
- `status` - scheduled | in_progress | completed | failed
- `outcome` - answered | no_answer | busy | failed | voicemail
- `duration_seconds` - Call length
- `tokens_consumed` - AI usage for billing
- `summary` - AI-generated call summary
- `transcript` - Full conversation text

**Relationships:**
- 1 Call → 1 AIAnalysis
- 1 Call → 1 CallRecording
- 1 Call → 1 CallCost
- 1 Call → Many WebhookDeliveries

**Indexes:**
- `(lead_id, status)`
- `(agent_id, status)`
- `(company_id, created_at)` - for analytics
- `(status, scheduled_at)` - for scheduler

---

### AIAnalysis
**Purpose:** AI processing results for calls
**Key Fields:**
- `sentiment` - positive | neutral | negative
- `sentiment_score` - -1.0 to 1.0
- `key_points` - JSON array of important topics
- `topics_discussed` - JSON array
- `objections_raised` - JSON array
- `intent_detected` - purchase_intent, information_gathering, etc.
- `next_actions` - JSON array of recommended follow-ups

**Relationship:** 1:1 with Call

---

### WebhookConfig
**Purpose:** Company webhook settings
**Key Fields:**
- `url` - Endpoint URL (HTTPS only)
- `event_call_started` - Subscribe to call.started
- `event_call_completed` - Subscribe to call.completed
- `event_call_analysed` - Subscribe to call.analysed
- `event_call_failed` - Subscribe to call.failed
- `secret_key` - For HMAC signature verification

**Relationship:** 1:1 with Company

---

### WebhookDelivery
**Purpose:** Webhook delivery log with retry logic
**Key Fields:**
- `event_type` - call.started, call.completed, etc.
- `payload` - JSON event data
- `status` - pending | success | failed | retrying
- `attempt_count` - Current retry attempt
- `max_attempts` - 4 (retry schedule: 1min, 5min, 15min, 1hr)
- `response_status_code` - HTTP response code
- `next_retry_at` - When to retry next

**Indexes:**
- `(status, next_retry_at)` - for retry worker

---

## Data Flow: Making a Call

```
1. Scheduler Job (runs every 1 minute)
   ↓
2. Query: SELECT * FROM leads WHERE status='scheduled' AND schedule_at <= NOW()
   ↓
3. Lock lead: UPDATE leads SET currently_in_call=true WHERE id=...
   ↓
4. Create Call record: INSERT INTO calls (status='in_progress')
   ↓
5. Trigger external Voice AI API
   ↓
6. Receive webhook: POST /webhooks/call-completed
   ↓
7. Update Call: status='completed', outcome='answered', duration=180
   ↓
8. Update Lead: attempts_count++, last_called_at=NOW(), currently_in_call=false
   ↓
9. Create AIAnalysis record (async background job)
   ↓
10. Create CallRecording (store S3 URL)
    ↓
11. Create CallCost (calculate billing)
    ↓
12. Create WebhookDelivery records (send to customer's webhook)
    ↓
13. Update CampaignDailyStats (increment counters)
    ↓
14. Create AuditLog entry
```

---

## Critical Indexes for Performance

### Hot Query 1: API Key Lookup
**Query:** `SELECT * FROM api_keys WHERE key_hash = ? AND is_active = true`
**Index:** `(key_hash)` UNIQUE

### Hot Query 2: Scheduled Calls
**Query:** `SELECT * FROM leads WHERE status='scheduled' AND schedule_at <= NOW()`
**Index:** `(status, schedule_at)`

### Hot Query 3: Company Dashboard
**Query:** `SELECT * FROM calls WHERE company_id = ? ORDER BY created_at DESC LIMIT 50`
**Index:** `(company_id, created_at DESC)`

### Hot Query 4: Webhook Retries
**Query:** `SELECT * FROM webhook_deliveries WHERE status IN ('pending', 'retrying') AND next_retry_at <= NOW()`
**Index:** `(status, next_retry_at)`

### Hot Query 5: Lead Search
**Query:** `SELECT * FROM leads WHERE phone_e164 = ? AND company_id = ?`
**Index:** `(company_id, phone_e164)`

---

## Data Retention & Cleanup

### Call Recordings
- Stored in S3 (not in database)
- `retain_until` field determines deletion date
- Default: 90 days retention
- Background job: `recording_cleanup_job` runs daily

### Soft Deletes
Models with soft delete:
- Lead (`deleted_at`, `deleted_by`)
- Campaign (`deleted_at`, `deleted_by`)
- Agent (`deleted_at`)

Advantage: Data recovery, audit compliance

---

## Multi-Tenancy Strategy

### Data Isolation
- Every model has `company_id` foreign key
- Django middleware enforces company filter on all queries
- API keys are scoped to company
- Row-level security (optional PostgreSQL RLS)

### Preventing Cross-Tenant Data Leaks
```python
# Good: Company filter enforced
leads = Lead.objects.filter(company=request.user.company)

# Bad: Missing company filter
leads = Lead.objects.filter(status='new')  # ❌ Exposes all companies
```

---

## Scaling Considerations

### Current Scale: < 1,000 calls/day
- Single PostgreSQL database
- Standard indexes sufficient
- No partitioning needed

### Future Scale: 10,000+ calls/day
- Consider:
  - Separate analytics database (read replica)
  - Partition `calls` table by created_at (monthly)
  - Cache hot queries in Redis
  - Archive old calls to data warehouse

---

## Background Jobs

### Celery/Django-Q Tasks

1. **call_scheduler_job** (every 1 min)
   - Find scheduled calls
   - Trigger voice AI platform

2. **webhook_retry_job** (every 5 min)
   - Retry failed webhook deliveries
   - Exponential backoff

3. **analytics_aggregation_job** (hourly)
   - Update CampaignDailyStats
   - Calculate success rates

4. **recording_cleanup_job** (daily)
   - Delete expired recordings from S3

5. **lead_status_sync_job** (every 15 min)
   - Mark leads as 'done' if max_attempts reached

---

## Security Best Practices

### API Keys
- **Never store plaintext keys**
- Store: `SHA256(key)` in `key_hash` field
- Show: Only `key_prefix` (first 12 chars) in UI
- Generate: `sk_live_` + random 32 chars

### Sensitive Data
- Consider encrypting `Lead.custom_fields` if contains PII
- Use Django's `EncryptedJSONField` from `django-encrypted-model-fields`

### Audit Logs
- Log all: CREATE, UPDATE, DELETE, VIEW, EXPORT actions
- Store: IP address, User-Agent, timestamp
- Retention: 1 year minimum for compliance

---

## Getting Started

### 1. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Create Superuser
```bash
python manage.py createsuperuser
```

### 3. Access Admin
```
http://localhost:8000/admin
```

All models are registered in Django Admin with custom views.

---

## Next Steps

1. **API Endpoints:** Create Django REST Framework serializers and viewsets
2. **Webhook Workers:** Implement Celery tasks for async processing
3. **Phone Verification:** Integrate Twilio Lookup API
4. **Voice AI Integration:** Connect to ElevenLabs/Google Cloud Speech
5. **Analytics Dashboard:** Build real-time metrics using CampaignDailyStats

---

## Questions?

This schema is designed to handle:
- ✅ Multi-tenant SaaS
- ✅ < 1,000 calls/day (can scale to 10K+ with optimizations)
- ✅ Standard compliance (GDPR/TCPA ready)
- ✅ One lead per campaign model

Built for: Valueloads AI Backend (ConversAI Labs inspired)
