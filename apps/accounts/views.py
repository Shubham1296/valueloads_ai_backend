from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import (
    CompanyRegisterSerializer,
    EmployeeRegisterSerializer,
    EmployeeSerializer,
    LoginSerializer,
    get_tokens_for_user,
)


class CompanyRegisterView(APIView):
    """Register a new company and its first admin employee."""
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Auth"],
        summary="Register company + admin",
        description="Creates a new company and its first admin employee. Returns JWT tokens.",
        request=CompanyRegisterSerializer,
        responses={201: OpenApiResponse(description="Company and tokens returned")},
        auth=[],
    )
    def post(self, request):
        serializer = CompanyRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company, employee = serializer.save()
        tokens = get_tokens_for_user(employee)
        return Response(
            {
                "company": {"id": str(company.id), "name": company.name, "slug": company.slug},
                "employee": EmployeeSerializer(employee).data,
                "tokens": tokens,
            },
            status=status.HTTP_201_CREATED,
        )


class EmployeeRegisterView(APIView):
    """Register a new employee under an existing company."""
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Auth"],
        summary="Register employee",
        description="Creates a new employee under an existing company identified by its slug.",
        request=EmployeeRegisterSerializer,
        responses={201: OpenApiResponse(description="Employee and tokens returned")},
        auth=[],
    )
    def post(self, request):
        serializer = EmployeeRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = serializer.save()
        tokens = get_tokens_for_user(employee)
        return Response(
            {
                "employee": EmployeeSerializer(employee).data,
                "tokens": tokens,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Authenticate an employee and return JWT tokens."""
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Auth"],
        summary="Login",
        description="Authenticate with email and password. Returns access and refresh JWT tokens.",
        request=LoginSerializer,
        responses={200: OpenApiResponse(description="Employee profile and tokens returned")},
        auth=[],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = serializer.validated_data["user"]
        tokens = get_tokens_for_user(employee)
        return Response(
            {
                "employee": EmployeeSerializer(employee).data,
                "tokens": tokens,
            }
        )


class MeView(APIView):
    """Return the currently authenticated employee's profile."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Profile"],
        summary="Get current user",
        description="Returns the profile of the currently authenticated employee.",
        responses={200: EmployeeSerializer},
    )
    def get(self, request):
        return Response(EmployeeSerializer(request.user).data)
