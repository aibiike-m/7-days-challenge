from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from .throttles import LoginRateThrottle

User = get_user_model()

@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
def exchange_token(request):
    try:
        token = request.data.get("credential") or request.data.get("access_token")
        language = request.data.get("language", "en")
        if not token:
            return Response({"error": "Token not provided"}, status=status.HTTP_400_BAD_REQUEST)
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY)
        email = idinfo.get("email")
        if not email:
            return Response({"error": "Email not found in token"}, status=status.HTTP_400_BAD_REQUEST)
        user, created = User.objects.get_or_create(email=email, defaults={"language": language})
        if created:
            user.set_unusable_password()
            user.save()
        if not created and user.language != language:
            user.language = language
            user.save(update_fields=["language"])
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "language": user.language,
            },
            "created": created,
        })
    except ValueError as e:
        return Response({"error": f"Invalid token: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
