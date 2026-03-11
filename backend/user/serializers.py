from rest_framework import serializers

from .email_verification import consume_email_code, validate_email_code
from .models import QualificationApplication, User


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "avatar", "role", "role_display"]


class RegisterSerializer(serializers.ModelSerializer):
    # Override default username field validators to allow common Chinese usernames.
    username = serializers.CharField(max_length=150, trim_whitespace=True)
    password = serializers.CharField(write_only=True)
    email_code = serializers.CharField(write_only=True, min_length=6, max_length=6)

    class Meta:
        model = User
        fields = ["username", "email", "password", "email_code"]

    def validate_username(self, value):
        username = value.strip()
        if not username:
            raise serializers.ValidationError("用户名不能为空")
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("用户名已存在")
        return username

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("邮箱已被使用")
        return value

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("密码长度不能少于6位")
        return value

    def validate_email_code(self, value):
        code = value.strip()
        if not code.isdigit() or len(code) != 6:
            raise serializers.ValidationError("验证码格式不正确")
        return code

    def validate(self, attrs):
        is_valid, message = validate_email_code(attrs["email"], attrs["email_code"])
        if not is_valid:
            raise serializers.ValidationError({"email_code": message})
        return attrs

    def create(self, validated_data):
        email = validated_data["email"]
        validated_data.pop("email_code", None)
        user = User.objects.create_user(**validated_data)
        consume_email_code(email)
        return user


class SendEmailCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("邮箱已被使用")
        return value


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserInfoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "avatar"]

    def validate_username(self, value):
        user = self.instance
        if user is None:
            return value
        if User.objects.exclude(id=user.id).filter(username=value).exists():
            raise serializers.ValidationError("用户名已存在")
        return value

    def validate_email(self, value):
        user = self.instance
        if user is None:
            return value
        if User.objects.exclude(id=user.id).filter(email=value).exists():
            raise serializers.ValidationError("邮箱已被使用")
        return value


class UserRoleListSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class UserRoleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["role"]


class QualificationApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualificationApplication
        fields = ["application_type", "reason"]

    def validate_reason(self, value):
        reason = value.strip()
        if not reason:
            raise serializers.ValidationError("申请说明不能为空")
        return reason


class QualificationApplicationSerializer(serializers.ModelSerializer):
    application_type_display = serializers.CharField(source="get_application_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = QualificationApplication
        fields = [
            "id",
            "application_type",
            "application_type_display",
            "reason",
            "status",
            "status_display",
            "review_note",
            "created_at",
            "reviewed_at",
        ]


class QualificationApplicationAdminSerializer(QualificationApplicationSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    user_role = serializers.CharField(source="user.role", read_only=True)
    reviewed_by_id = serializers.IntegerField(source="reviewed_by.id", read_only=True)
    reviewed_by_username = serializers.CharField(source="reviewed_by.username", read_only=True)

    class Meta(QualificationApplicationSerializer.Meta):
        fields = QualificationApplicationSerializer.Meta.fields + [
            "user_id",
            "username",
            "user_role",
            "reviewed_by_id",
            "reviewed_by_username",
        ]


class QualificationApplicationReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            QualificationApplication.STATUS_APPROVED,
            QualificationApplication.STATUS_REJECTED,
        ]
    )
    review_note = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs["status"] == QualificationApplication.STATUS_REJECTED and not attrs.get("review_note", "").strip():
            raise serializers.ValidationError({"review_note": "驳回时请填写审核备注"})
        return attrs
