from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if User.objects.filter(username=username).exists():
            return Response({"error": "Пользователь существует"}, status=400)

        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        return Response({"success": True}, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    def post(self, request):
        response = Response({"message": "Logged out"})
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        return response
