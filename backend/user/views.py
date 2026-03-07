from .address_models import Address
from .address_serializers import AddressSerializer
from rest_framework import generics

# 地址列表与创建
class AddressListCreateView(generics.ListCreateAPIView):
	serializer_class = AddressSerializer
	permission_classes = [IsAuthenticated]
	def get_queryset(self):
		return Address.objects.filter(user=self.request.user)
	def list(self, request, *args, **kwargs):
		queryset = self.get_queryset()
		serializer = self.get_serializer(queryset, many=True)
		return Response({'code': 0, 'message': 'ok', 'data': serializer.data})
	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		if serializer.validated_data.get('is_default'):
			Address.objects.filter(user=self.request.user, is_default=True).update(is_default=False)
		serializer.save(user=self.request.user)
		return Response({'code': 0, 'message': 'ok', 'data': serializer.data}, status=201)

# 地址详情、更新、删除
class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
	serializer_class = AddressSerializer
	permission_classes = [IsAuthenticated]
	def get_queryset(self):
		return Address.objects.filter(user=self.request.user)
	def retrieve(self, request, *args, **kwargs):
		instance = self.get_object()
		serializer = self.get_serializer(instance)
		return Response({'code': 0, 'message': 'ok', 'data': serializer.data})
	def update(self, request, *args, **kwargs):
		partial = kwargs.pop('partial', False)
		instance = self.get_object()
		serializer = self.get_serializer(instance, data=request.data, partial=partial)
		serializer.is_valid(raise_exception=True)
		if serializer.validated_data.get('is_default'):
			Address.objects.filter(user=self.request.user, is_default=True).update(is_default=False)
		serializer.save()
		return Response({'code': 0, 'message': 'ok', 'data': serializer.data})
	def destroy(self, request, *args, **kwargs):
		instance = self.get_object()
		instance.delete()
		return Response({'code': 0, 'message': 'ok'})
from rest_framework.permissions import IsAuthenticated

class UserInfoView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request):
		user = request.user
		return Response({'code': 0, 'message': 'ok', 'data': UserSerializer(user).data})

	def put(self, request):
		user = request.user
		serializer = UserSerializer(user, data=request.data, partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response({'code': 0, 'message': 'ok', 'data': serializer.data})
		return Response({'code': 1005, 'message': '更新失败', 'errors': serializer.errors}, status=400)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from django.contrib.auth import authenticate

def jwt_response_payload_handler(token, user=None, request=None):
	return {
		'code': 0,
		'message': 'ok',
		'data': {
			'token': str(token),
			'user': UserSerializer(user).data if user else None
		}
	}

class RegisterView(APIView):
	def post(self, request):
		serializer = RegisterSerializer(data=request.data)
		if serializer.is_valid():
			user = User(
				username=serializer.validated_data['username'],
				email=serializer.validated_data['email']
			)
			user.encrypt_password(serializer.validated_data['password'])
			user.save()
			refresh = RefreshToken.for_user(user)
			return Response(jwt_response_payload_handler(refresh.access_token, user), status=status.HTTP_201_CREATED)
		return Response({'code': 1001, 'message': '注册失败', 'errors': serializer.errors}, status=400)

class LoginView(APIView):
	def post(self, request):
		serializer = LoginSerializer(data=request.data)
		if serializer.is_valid():
			username = serializer.validated_data['username']
			password = serializer.validated_data['password']
			try:
				user = User.objects.get(username=username)
			except User.DoesNotExist:
				return Response({'code': 1002, 'message': '用户不存在'}, status=400)
			if user.check_password(password):
				refresh = RefreshToken.for_user(user)
				return Response(jwt_response_payload_handler(refresh.access_token, user), status=200)
			return Response({'code': 1003, 'message': '密码错误'}, status=400)
		return Response({'code': 1004, 'message': '参数错误', 'errors': serializer.errors}, status=400)
