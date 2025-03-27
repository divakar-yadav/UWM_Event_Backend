from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import renderers
from .UserSerializer import UserSerializer
from rest_framework import status
# from rest_framework_simplejwt.tokens import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User


class Signup(APIView):

    renderer_classes = [renderers.JSONRenderer]

    def post(self, request):
        print(request.data)

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():

            try:
                new_user = serializer.save()
            except:
                return Response({'success': False, 'message': 'User registration failed.', 'errors': {'Email': 'User already exists.'}}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'success': True, 'message': 'User registered successfully.', 'user_id': new_user.id}, status=status.HTTP_201_CREATED)
        else:
            # instead of serializer.errors, we can send the list of errors
            # to the user
            print(serializer.errors)
            return Response({'success': False, 'message': 'User registration failed.', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
