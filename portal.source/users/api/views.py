from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password

from rest_framework import generics, status
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from users.models import Consumer, Profile
from . import serializers
from users.api.models import MyOwnToken


class ConsumerView(generics.ListAPIView):
    queryset = Consumer.objects.all()
    serializer_class = serializers.ConsumerSerializer


@api_view(['GET', ])
def api_detail_consumer_view(request, id):

    try:
        con = Consumer.objects.get(id=id)

    except Consumer.DoesNotExists:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = serializers.ConsumerSerializer(con)
        return Response(serializer.data)


@api_view(['POST', ])
def api_consumer_register_view(request):
    if request.method == "POST":
        serializer = serializers.ConsumerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            consumer = serializer.save()

            token = MyOwnToken.objects.create(consumer=consumer)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
def api_product_check_view(request):
    if request.method == "POST":
        serializer = serializers.ProductSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.initial_data.get('token')
            try:
                con = MyOwnToken.objects.get(key=token)
            except MyOwnToken.DoesNotExist:
                return Response(data={'response': "Consumer Does Not Exists"}, status=status.HTTP_404_NOT_FOUND)
            consumer = Consumer.objects.get(id=con.consumer_id)
            data = {
                'response': "Product Patched Successfully",
                'token': token,
                'consumer_name': consumer.con_name,
                'consumer_email': consumer.email,
            }
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
def api_retailer_login_view(request):
    if request.method == "POST":
        serializer = serializers.RetailerSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.initial_data.get('token')
            username = serializer.initial_data.get('username')
            password = serializer.initial_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                try:
                    tok = Token.objects.get(user=user)
                    if tok.key == token or token == '':
                        return Response({'token': tok.key}, status=status.HTTP_200_OK)
                    else:
                        return Response({'response': "UNAUTHORIZED Token"}, status=status.HTTP_401_UNAUTHORIZED)
                except Token.DoesNotExist:
                    tok = Token.objects.create(user=user)
                    return Response({'token': tok.key}, status=status.HTTP_201_CREATED)
            else:
                try:
                    return Response({'response': "Password Mismatch"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                except User.DoesNotExist:
                    return Response({'response': "Retailer Not Found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
def api_agent_register_view(request):
    if request.method == 'POST':
        serializer = serializers.AgentRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            phone = serializer.initial_data.get('phone')

            token = Token.objects.create(user=user)

            profile = Profile.objects.get(user_id=user.id)
            profile.phone = phone
            profile.user_token = token.key
            profile.status = 'ACTIVE'
            profile.force_login = True
            profile.save()
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', ])
@permission_classes([IsAuthenticated])
def api_agent_update_view(request):
    if request.method == 'PUT':
        serializer = serializers.AgentUpdateSerializer(instance=request.user, data=request.data)
        if serializer.is_valid():
            username = serializer.initial_data.get('username')
            try:
                user = User.objects.get(username=username)
                token = Token.objects.get(user=user)
            except User.DoesNotExist:
                return Response({'User': 'Agent Not Found'}, status.HTTP_404_NOT_FOUND)
            if request.user == user:
                serializer.save()
            else:
                return Response({'response': 'Agent Not Acceptable'}, status.HTTP_406_NOT_ACCEPTABLE)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AgentChangePasswordView(UpdateAPIView):
    serializer_class = serializers.AgentChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        if hasattr(user, 'auth_token'):
            user.auth_token.delete()
        token, created = Token.objects.get_or_create(user=user)
        profile = Profile.objects.get(user_id=user.id)
        profile.user_token = token.key
        profile.save()
        return Response({'token': token.key}, status=status.HTTP_200_OK)


@api_view(['POST', ])
def api_consumer_login_view(request):
    if request.method == "POST":
        serializer = serializers.ConsumerLoginSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.initial_data.get('token')
            username = serializer.initial_data.get('username')
            password = serializer.initial_data.get('password')
            try:
                consumer = Consumer.objects.get(username=username)
                if check_password(password=password, encoded=consumer.password):
                    try:
                        tok = MyOwnToken.objects.get(consumer=consumer)
                        if tok.key == token or token == '':
                            return Response({'token': tok.key}, status=status.HTTP_200_OK)
                        else:
                            return Response({'response': "Invalid Token"}, status=status.HTTP_401_UNAUTHORIZED)
                    except MyOwnToken.DoesNotExist:
                        tok = MyOwnToken.objects.create(consumer=consumer)
                        return Response({'token': tok.key}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'response': "Password Mismatch"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            except Consumer.DoesNotExist:
                return Response({'response': "Consumer Not Found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)