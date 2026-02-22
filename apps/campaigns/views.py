from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Campaign
from .serializers import CampaignSerializer


class CampaignListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Campaigns"],
        summary="List campaigns",
        description="Returns all campaigns.",
        responses={200: CampaignSerializer(many=True)},
    )
    def get(self, request):
        campaigns = Campaign.objects.all()
        return Response(CampaignSerializer(campaigns, many=True).data)

    @extend_schema(
        tags=["Campaigns"],
        summary="Create campaign",
        description="Creates a new campaign. The authenticated employee is recorded as the creator.",
        request=CampaignSerializer,
        responses={
            201: CampaignSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
    )
    def post(self, request):
        serializer = CampaignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CampaignDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, uuid):
        try:
            return Campaign.objects.get(uuid=uuid)
        except Campaign.DoesNotExist:
            return None

    @extend_schema(
        tags=["Campaigns"],
        summary="Retrieve campaign",
        description="Returns a single campaign by UUID.",
        responses={
            200: CampaignSerializer,
            404: OpenApiResponse(description="Not found"),
        },
    )
    def get(self, request, uuid):
        campaign = self.get_object(uuid)
        if campaign is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(CampaignSerializer(campaign).data)

    @extend_schema(
        tags=["Campaigns"],
        summary="Update campaign",
        description="Fully updates a campaign. The authenticated employee is recorded as the last updater.",
        request=CampaignSerializer,
        responses={
            200: CampaignSerializer,
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Not found"),
        },
    )
    def put(self, request, uuid):
        campaign = self.get_object(uuid)
        if campaign is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CampaignSerializer(campaign, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data)

    @extend_schema(
        tags=["Campaigns"],
        summary="Partial update campaign",
        description="Partially updates a campaign. The authenticated employee is recorded as the last updater.",
        request=CampaignSerializer,
        responses={
            200: CampaignSerializer,
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Not found"),
        },
    )
    def patch(self, request, uuid):
        campaign = self.get_object(uuid)
        if campaign is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CampaignSerializer(campaign, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data)

    @extend_schema(
        tags=["Campaigns"],
        summary="Delete campaign",
        description="Deletes a campaign by UUID.",
        responses={
            204: OpenApiResponse(description="Deleted"),
            404: OpenApiResponse(description="Not found"),
        },
    )
    def delete(self, request, uuid):
        campaign = self.get_object(uuid)
        if campaign is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        campaign.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
