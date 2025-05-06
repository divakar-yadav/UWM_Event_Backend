# this login will use Django rest framework to authenticate users
# and assign them a jwt token and return it to the user
# this will be used to authenticate users for the rest of the app
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import renderers
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import check_password

class Login(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer
    renderer_classes = [renderers.JSONRenderer]

    def post(self, request, *args, **kwargs):
        try:
            email = request.data['email']
            password = request.data['password']
        except:
            return Response({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)
        if not email or not password:
            return Response({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)

        User = get_user_model()

        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password):
                pass
            elif user.password == password:
                #raise User.DoesNotExist
                pass
            else:
                raise User.DoesNotExist
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_404_NOT_FOUND)

        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_404_NOT_FOUND)
        # set CST timezone
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        token = TokenObtainPairSerializer.get_token(user)
        return Response({'token': str(token.access_token), 'user_id': user.id, 'email': user.email, 'first_name' : user.first_name}, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def current_user(request):
    return Response({
        "first_name": request.user.first_name,
        "email": request.user.email,
        "is_superuser": request.user.is_superuser
    })