# API Endpoints Documentation

## 🚀 Quick Start

### Base URL
```
http://localhost:8000/api
```

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

---

## 🔐 Authentication

All endpoints require JWT Bearer token authentication.

### Obtain Token
```http
POST /api/auth/token/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Use Token
```http
GET /api/agents/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## 📋 API Endpoints Overview

### 🤖 Agents (`/api/agents/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/agents/` | List all agents with filtering |
| POST | `/agents/` | Create new agent |
| GET | `/agents/{id}/` | Get agent details |
| PUT | `/agents/{id}/` | Update agent |
| PATCH | `/agents/{id}/` | Partial update |
| DELETE | `/agents/{id}/` | Soft delete agent |
| GET | `/agents/{id}/versions/` | Get agent version history |
| GET | `/agents/{id}/performance/` | Get agent performance metrics |

**Filters**: `company`, `campaign`, `status`
**Search**: `name`, `description`
**Ordering**: `created_at`, `name`, `total_calls`

#### Voice Configurations (`/api/voice-configs/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/voice-configs/` | List voice configurations |
| POST | `/voice-configs/` | Create voice config |
| GET | `/voice-configs/{id}/` | Get config details |
| PUT | `/voice-configs/{id}/` | Update config |
| DELETE | `/voice-configs/{id}/` | Delete config |

---

### 🎯 Leads (`/api/leads/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/leads/` | List all leads with filtering |
| POST | `/leads/` | Create new lead |
| GET | `/leads/{id}/` | Get lead details |
| PUT | `/leads/{id}/` | Update lead |
| PATCH | `/leads/{id}/` | Partial update |
| DELETE | `/leads/{id}/` | Soft delete lead |
| POST | `/leads/{id}/add_note/` | Add note to lead |
| GET | `/leads/{id}/call_history/` | Get call history |

**Filters**: `company`, `agent`, `campaign`, `status`, `disposition`, `is_verified`
**Search**: `first_name`, `last_name`, `phone_e164`, `email`
**Ordering**: `created_at`, `last_called_at`, `schedule_at`, `lead_score`

#### Lead Import Batches (`/api/import-batches/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/import-batches/` | List import jobs |
| POST | `/import-batches/` | Create import job |
| GET | `/import-batches/{id}/` | Get batch details |

#### Lead Notes (`/api/notes/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/notes/` | List notes |
| POST | `/notes/` | Create note |
| GET | `/notes/{id}/` | Get note |
| PUT | `/notes/{id}/` | Update note |
| DELETE | `/notes/{id}/` | Delete note |

---

### 📞 Calls (`/api/calls/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/calls/` | List all calls |
| POST | `/calls/` | Create call record |
| GET | `/calls/{id}/` | Get call details with AI analysis |
| PUT | `/calls/{id}/` | Update call |
| PATCH | `/calls/{id}/` | Partial update |
| GET | `/calls/metrics/` | Get aggregate call metrics |

**Filters**: `company`, `agent`, `lead`, `status`, `outcome`
**Search**: `lead__first_name`, `lead__last_name`, `lead__phone_e164`
**Ordering**: `created_at`, `started_at`, `duration_seconds`

#### AI Analysis (`/api/ai-analysis/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/ai-analysis/` | List AI analyses |
| GET | `/ai-analysis/{id}/` | Get analysis details |

**Filters**: `call`, `sentiment`

#### Call Recordings (`/api/recordings/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/recordings/` | List recordings |
| GET | `/recordings/{id}/` | Get recording metadata |

**Filters**: `call`, `is_deleted`, `format`

#### Call Costs (`/api/costs/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/costs/` | List call costs |
| GET | `/costs/{id}/` | Get cost details |
| GET | `/costs/total_costs/` | Get total costs aggregated |

**Filters**: `call`, `voice_provider`, `ai_provider`

---

### 📊 Campaigns (`/api/campaigns/`)

Existing campaign endpoints remain unchanged.

---

### 🔔 Webhooks (`/api/webhooks/`)

#### Webhook Configs (`/api/webhooks/configs/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/webhooks/configs/` | List webhook configs |
| POST | `/webhooks/configs/` | Create config |
| GET | `/webhooks/configs/{id}/` | Get config details |
| PUT | `/webhooks/configs/{id}/` | Update config |
| DELETE | `/webhooks/configs/{id}/` | Delete config |
| POST | `/webhooks/configs/{id}/test/` | Send test webhook |

**Filters**: `company`, `is_active`

#### Webhook Deliveries (`/api/webhooks/deliveries/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/webhooks/deliveries/` | List delivery logs |
| GET | `/webhooks/deliveries/{id}/` | Get delivery details |
| POST | `/webhooks/deliveries/{id}/retry/` | Manually retry failed delivery |

**Filters**: `webhook_config`, `call`, `event_type`, `status`

---

### 🔌 Integrations (`/api/integrations/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/integrations/` | List integrations |
| POST | `/integrations/` | Create integration |
| GET | `/integrations/{id}/` | Get integration details |
| PUT | `/integrations/{id}/` | Update integration |
| DELETE | `/integrations/{id}/` | Delete integration |
| POST | `/integrations/{id}/sync/` | Trigger sync |
| GET | `/integrations/{id}/logs/` | Get sync logs |

**Filters**: `company`, `integration_type`, `is_active`
**Search**: `name`

#### Integration Logs (`/api/logs/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/logs/` | List integration logs |
| GET | `/logs/{id}/` | Get log details |

**Filters**: `integration`, `action`, `success`

---

### 💾 Data Exports (`/api/exports/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/exports/` | List export jobs |
| POST | `/exports/` | Create export job |
| GET | `/exports/{id}/` | Get export details |
| GET | `/exports/{id}/download/` | Get download URL |

**Filters**: `company`, `export_type`, `status`, `requested_by`

---

## 📝 Example Requests

### Create Agent
```bash
curl -X POST http://localhost:8000/api/agents/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sales Agent",
    "company": "uuid-here",
    "campaign": "uuid-here",
    "status": "active",
    "prompt": "You are a friendly sales representative...",
    "welcome_message": "Hi, this is Sarah calling from Acme Corp",
    "max_attempts": 3,
    "model_name": "gpt-4-turbo",
    "temperature": 0.7
  }'
```

### Create Lead
```bash
curl -X POST http://localhost:8000/api/leads/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "phone_e164": "+14155552671",
    "email": "john@example.com",
    "company": "uuid-here",
    "agent": "uuid-here",
    "campaign": "uuid-here",
    "status": "new",
    "custom_fields": {
      "company": "Acme Corp",
      "title": "CTO"
    }
  }'
```

### Get Call Metrics
```bash
curl -X GET "http://localhost:8000/api/calls/metrics/?company=uuid-here&status=completed" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "total_calls": 1250,
  "total_answered": 875,
  "avg_duration": 180.5,
  "total_duration": 225625,
  "total_tokens": 45000,
  "answer_rate": 70.0
}
```

### Configure Webhook
```bash
curl -X POST http://localhost:8000/api/webhooks/configs/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "uuid-here",
    "url": "https://your-app.com/webhooks/calls",
    "is_active": true,
    "event_call_started": true,
    "event_call_completed": true,
    "event_call_analysed": true,
    "event_call_failed": true,
    "secret_key": "your-secret-key"
  }'
```

---

## 🔍 Filtering & Searching

### Filter by Multiple Fields
```
GET /api/leads/?status=new&agent=uuid-here&campaign=uuid-here
```

### Search
```
GET /api/leads/?search=john+doe
```

### Ordering
```
GET /api/calls/?ordering=-created_at  # Descending
GET /api/leads/?ordering=lead_score   # Ascending
```

### Pagination
```
GET /api/agents/?page=2&page_size=50
```

---

## 🏷️ Status & Enum Values

### Agent Status
- `active` - Agent is active
- `inactive` - Agent is paused
- `testing` - Agent in testing mode

### Lead Status
- `new` - New lead
- `scheduled` - Call scheduled
- `in_progress` - Currently being called
- `done` - All attempts complete
- `stopped` - Manually stopped

### Lead Disposition
- `not_interested` - Not interested
- `hung_up` - Hung up
- `completed` - Successfully completed
- `no_answer` - No answer
- `callback_requested` - Requested callback
- `voicemail` - Voicemail left
- `wrong_number` - Wrong number
- `dnc` - Do not call

### Call Status
- `scheduled` - Scheduled
- `in_progress` - In progress
- `completed` - Completed
- `failed` - Failed

### Call Outcome
- `answered` - Answered
- `no_answer` - No answer
- `busy` - Busy
- `failed` - Failed
- `voicemail` - Voicemail

---

## 🚀 Testing

### Run Server
```bash
python manage.py runserver
```

### Access Swagger UI
Open browser: http://localhost:8000/api/docs/

---

## 📊 Total API Endpoints

- **Agents**: 11 endpoints
- **Leads**: 13 endpoints
- **Calls**: 14 endpoints
- **Webhooks**: 7 endpoints
- **Integrations**: 7 endpoints
- **Exports**: 4 endpoints
- **Total**: 56+ endpoints

All endpoints support JWT authentication and include comprehensive filtering, searching, and pagination!
