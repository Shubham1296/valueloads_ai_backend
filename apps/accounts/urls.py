from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import CompanyRegisterView, EmployeeRegisterView, LoginView, MeView

urlpatterns = [
    path("company/register/", CompanyRegisterView.as_view(), name="company-register"),
    path("employee/register/", EmployeeRegisterView.as_view(), name="employee-register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="me"),
]
