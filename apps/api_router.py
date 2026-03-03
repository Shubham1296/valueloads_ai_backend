"""
Central API router that consolidates all viewsets
"""
from rest_framework.routers import DefaultRouter
from apps.agents.views import VoiceConfigurationViewSet, AgentViewSet, AgentVersionViewSet
from apps.leads.views import LeadViewSet, LeadImportBatchViewSet, LeadNoteViewSet
from apps.calls.views import CallViewSet, AIAnalysisViewSet, CallRecordingViewSet, CallCostViewSet
from apps.webhooks.views import WebhookConfigViewSet, WebhookDeliveryViewSet
from apps.integrations.views import IntegrationViewSet, IntegrationLogViewSet
from apps.exports.views import DataExportViewSet

# Create main router
router = DefaultRouter()

# Agents
router.register(r'voice-configs', VoiceConfigurationViewSet, basename='voiceconfiguration')
router.register(r'agents', AgentViewSet, basename='agent')
router.register(r'agent-versions', AgentVersionViewSet, basename='agentversion')

# Leads
router.register(r'leads', LeadViewSet, basename='lead')
router.register(r'lead-import-batches', LeadImportBatchViewSet, basename='leadimportbatch')
router.register(r'lead-notes', LeadNoteViewSet, basename='leadnote')

# Calls
router.register(r'calls', CallViewSet, basename='call')
router.register(r'ai-analysis', AIAnalysisViewSet, basename='aianalysis')
router.register(r'call-recordings', CallRecordingViewSet, basename='callrecording')
router.register(r'call-costs', CallCostViewSet, basename='callcost')

# Webhooks
router.register(r'webhook-configs', WebhookConfigViewSet, basename='webhookconfig')
router.register(r'webhook-deliveries', WebhookDeliveryViewSet, basename='webhookdelivery')

# Integrations
router.register(r'integrations', IntegrationViewSet, basename='integration')
router.register(r'integration-logs', IntegrationLogViewSet, basename='integrationlog')

# Exports
router.register(r'data-exports', DataExportViewSet, basename='dataexport')
