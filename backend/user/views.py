from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from typing import cast
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .address_serializers import AddressSerializer
from .email_verification import can_resend_email_code, generate_email_code, store_email_code
from .models import Address, QualificationApplication, User
from .serializers import (
    QualificationApplicationAdminSerializer,
    QualificationApplicationCreateSerializer,
    QualificationApplicationReviewSerializer,
    QualificationApplicationSerializer,
    LoginSerializer,
    RegisterSerializer,
    SendEmailCodeSerializer,
    UserRoleListSerializer,
    UserRoleUpdateSerializer,
    UserInfoUpdateSerializer,
    UserSerializer,
)


def build_token_response(user, status_code=status.HTTP_200_OK):
    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "code": 0,
            "message": "ok",
            "data": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            },
        },
        status=status_code,
    )


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return build_token_response(user, status.HTTP_201_CREATED)


class SendRegisterEmailCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendEmailCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = cast(str, serializer.validated_data["email"])
        if not can_resend_email_code(email):
            return Response({"code": 1012, "message": "发送过于频繁，请60秒后重试"}, status=status.HTTP_400_BAD_REQUEST)

        code = generate_email_code()
        try:
            send_mail(
                subject="商城注册验证码",
                message=f"您的注册验证码是：{code}，5分钟内有效。",
                from_email=getattr(settings, "EMAIL_HOST_USER", None),
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception:
            return Response({"code": 1013, "message": "验证码发送失败，请稍后再试"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        store_email_code(email, code)
        return Response({"code": 0, "message": "验证码已发送"})


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        credentials = cast(dict[str, str], serializer.validated_data)
        username = credentials.get("username")
        password = credentials.get("password")
        if not username or not password:
            return Response({"code": 1004, "message": "参数错误"}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({"code": 1002, "message": "用户名或密码错误"}, status=status.HTTP_400_BAD_REQUEST)

        return build_token_response(user)


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"code": 0, "message": "ok", "data": UserSerializer(request.user).data})

    def put(self, request):
        serializer = UserInfoUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"code": 0, "message": "ok", "data": UserSerializer(request.user).data})


class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response({"code": 0, "message": "ok", "data": serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        should_default = serializer.validated_data.get("is_default", False)
        if not request.user.addresses.exists():
            should_default = True

        if should_default:
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)

        address = serializer.save(user=request.user, is_default=should_default)
        return Response(
            {"code": 0, "message": "ok", "data": self.get_serializer(address).data},
            status=status.HTTP_201_CREATED,
        )


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response({"code": 0, "message": "ok", "data": serializer.data})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data.get("is_default"):
            Address.objects.filter(user=request.user, is_default=True).exclude(id=instance.id).update(is_default=False)

        address = serializer.save()
        return Response({"code": 0, "message": "ok", "data": self.get_serializer(address).data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        was_default = instance.is_default
        instance.delete()

        if was_default:
            next_address = Address.objects.filter(user=request.user).first()
            if next_address:
                next_address.is_default = True
                next_address.save(update_fields=["is_default"])

        return Response({"code": 0, "message": "ok"}, status=status.HTTP_200_OK)


class AddressSetDefaultView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            address = Address.objects.get(pk=pk, user=request.user)
        except Address.DoesNotExist:
            return Response({"code": 1006, "message": "地址不存在"}, status=status.HTTP_404_NOT_FOUND)

        Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
        address.is_default = True
        address.save(update_fields=["is_default"])
        return Response({"code": 0, "message": "ok", "data": AddressSerializer(address).data})


class RoleListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        roles = [{"value": value, "label": label} for value, label in request.user.ROLE_CHOICES]
        serializer = UserRoleListSerializer(roles, many=True)
        return Response({"code": 0, "message": "ok", "data": serializer.data})


class AdminUserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_admin_role:
            return Response({"code": 1003, "message": "权限不足"}, status=status.HTTP_403_FORBIDDEN)

        users = UserSerializer(User.objects.all().order_by("id"), many=True)
        return Response({"code": 0, "message": "ok", "data": users.data})


class AdminUserRoleUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        if not request.user.is_admin_role:
            return Response({"code": 1003, "message": "权限不足"}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"code": 1007, "message": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserRoleUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"code": 0, "message": "ok", "data": UserSerializer(user).data})


class QualificationApplicationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        applications = QualificationApplication.objects.filter(user=request.user)
        serializer = QualificationApplicationSerializer(applications, many=True)
        return Response({"code": 0, "message": "ok", "data": serializer.data})

    def post(self, request):
        serializer = QualificationApplicationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = cast(dict[str, str], serializer.validated_data)
        application_type = payload["application_type"]
        if QualificationApplication.objects.filter(
            user=request.user,
            application_type=application_type,
            status=QualificationApplication.STATUS_PENDING,
        ).exists():
            return Response({"code": 1010, "message": "已有同类型待审核申请，请勿重复提交"}, status=status.HTTP_400_BAD_REQUEST)

        application = serializer.save(user=request.user)
        return Response(
            {"code": 0, "message": "ok", "data": QualificationApplicationSerializer(application).data},
            status=status.HTTP_201_CREATED,
        )


class AdminQualificationApplicationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_admin_role:
            return Response({"code": 1003, "message": "权限不足"}, status=status.HTTP_403_FORBIDDEN)

        queryset = QualificationApplication.objects.select_related("user", "reviewed_by").all()

        status_value = request.query_params.get("status")
        type_value = request.query_params.get("application_type")
        user_id_value = request.query_params.get("user_id")

        if status_value:
            queryset = queryset.filter(status=status_value)
        if type_value:
            queryset = queryset.filter(application_type=type_value)
        if user_id_value:
            queryset = queryset.filter(user_id=user_id_value)

        serializer = QualificationApplicationAdminSerializer(queryset, many=True)
        return Response({"code": 0, "message": "ok", "data": serializer.data})


class AdminQualificationApplicationReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not request.user.is_admin_role:
            return Response({"code": 1003, "message": "权限不足"}, status=status.HTTP_403_FORBIDDEN)

        try:
            application = QualificationApplication.objects.select_related("user", "reviewed_by").get(pk=pk)
        except QualificationApplication.DoesNotExist:
            return Response({"code": 1008, "message": "资质申请不存在"}, status=status.HTTP_404_NOT_FOUND)

        if application.status != QualificationApplication.STATUS_PENDING:
            return Response({"code": 1011, "message": "该申请已审核，不能重复审核"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = QualificationApplicationReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = cast(dict[str, str], serializer.validated_data)
        review_status = payload["status"]
        review_note = payload.get("review_note", "").strip()

        application.status = review_status
        application.review_note = review_note
        application.reviewed_by = request.user
        application.reviewed_at = timezone.now()
        application.save(update_fields=["status", "review_note", "reviewed_by", "reviewed_at", "updated_at"])

        # 商家申请通过后自动授予商家角色；工作人员申请只做资质记录。
        if (
            application.application_type == QualificationApplication.TYPE_MERCHANT
            and review_status == QualificationApplication.STATUS_APPROVED
            and application.user.role != User.ROLE_ADMIN
        ):
            application.user.role = User.ROLE_MERCHANT
            application.user.save(update_fields=["role", "is_staff"])

        application.refresh_from_db()
        return Response({"code": 0, "message": "ok", "data": QualificationApplicationAdminSerializer(application).data})
