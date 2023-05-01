from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import redirect

from drf_yasg.utils import swagger_auto_schema

from rest_framework import status, permissions
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404, UpdateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet


from .models import *
from .serializers import *


User = get_user_model()


class RegisterAPIView(APIView):
    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                'Account created. Please check your email to activate your account.'
            )


@api_view(["GET"])
def activate(request, activation_code):
    user = get_object_or_404(User, activation_code=activation_code)
    user.is_active = True
    user.activation_code = ''
    user.save()
    return redirect("http://127.0.0.1:8000/docs/")


class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = [IsAuthenticated, ] 

    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def update(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not user.check_password(request.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(request.data.get("new_password"))
            user.is_active = True
            user.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully'
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    @swagger_auto_schema(request_body=ForgotSerializer)
    def post(self, request):
        data = request.POST
        serializer = ForgotSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            message = "Please, check your email"
            return Response(message)

class NewPasswordView(APIView):
    def get(self, request, activation_code):
        user = get_object_or_404(User, activation_code=activation_code)
        new_password = user.generate_activation_code()
        user.set_password(new_password)
        user.save()
        return Response(f"Your new password is {new_password}")

class LogoutAPIView(GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        serializers = self.serializer_class(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save()
        return Response(
            {"msg":"You successfully logged out"}, 
            status=status.HTTP_204_NO_CONTENT
        )
