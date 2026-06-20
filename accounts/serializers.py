from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from accounts.models import Profile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')
        read_only_fields = ('id',)


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    city_display = serializers.CharField(source='get_city_display', read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            'id', 'user', 'role', 'role_display',
            'phone', 'city', 'city_display',
            'bio', 'avatar', 'avatar_url', 'created_at',
        )
        read_only_fields = ('id', 'created_at')

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None


class UserRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=False, default='')
    last_name = serializers.CharField(max_length=150, required=False, default='')
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(
        write_only=True, 
        min_length=8, 
        max_length=30,
        error_messages={
            'min_length': 'Parol kamida 8 ta belgidan iborat bo\'lishi kerak!',
            'max_length': 'Parol 30 ta belgidan oshmasligi kerak!'
        }
    )
    re_password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=Profile.ROLE_CHOICES, default='client')

    def validate_username(self, value):
        import re
        if not re.match(r'^[a-z0-9_]+$', value):
            raise serializers.ValidationError("Username faqat kichik lotin harflari, raqamlar va '_' belgisidan iborat bo'lishi mumkin!")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Bu username allaqachon band!")
        return value

    def validate(self, data):
        if data['password'] != data['re_password']:
            raise serializers.ValidationError({'re_password': "Parollar mos emas!"})
        return data

    def create(self, validated_data):
        validated_data.pop('re_password')
        role = validated_data.pop('role', 'client')

        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password'],
        )
        Profile.objects.filter(user=user).update(role=role)
        return user


class UserSecondRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=True, error_messages={'required': 'Telefon raqamini kiritish majburiy!', 'blank': 'Telefon raqamini kiritish majburiy!'})

    class Meta:
        model = Profile
        fields = ('bio', 'avatar', 'city', 'phone', 'email')

    def validate_email(self, value):
        if value and self.instance and User.objects.exclude(pk=self.instance.user.pk).filter(email=value).exists():
            raise serializers.ValidationError("Bu email allaqachon band!")
        return value

    def update(self, instance, validated_data):
        email = validated_data.pop('email', None)
        if email is not None:
            instance.user.email = email
            instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username:
            raise serializers.ValidationError({'username': 'Username kiritish majburiy!'})
        if not password:
            raise serializers.ValidationError({'password': 'Parol kiritish majburiy!'})

        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError(
                {'non_field_errors': 'Username yoki parol noto\'g\'ri!'}
            )
        if not user.is_active:
            raise serializers.ValidationError(
                {'non_field_errors': 'Akkaunt faol emas!'}
            )

        data['user'] = user
        return data
