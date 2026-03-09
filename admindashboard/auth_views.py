from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.utils import timezone

User = get_user_model()

def _token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

@api_view(["POST"])
@permission_classes([AllowAny])
def dashboard_signin(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {"detail": "Please provide both email and password"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = User.objects.get(email=email)

        if check_password(password, user.password):
            pass
        elif user.password == password:
            pass
        else:
            raise User.DoesNotExist

    except User.DoesNotExist:
        return Response(
            {"detail": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    allowed = user.is_superuser or user.groups.filter(name="DashboardAccess").exists()
    if not allowed:
        return Response(
            {"detail": "Not authorized for dashboard"},
            status=status.HTTP_403_FORBIDDEN,
        )

    user.last_login = timezone.now()
    user.save(update_fields=["last_login"])

    tokens = _token_for_user(user)
    return Response(
        {
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "first_name": user.first_name,
            "email": user.email,
            "can_access_dashboard": True,
        },
        status=status.HTTP_200_OK,
    )