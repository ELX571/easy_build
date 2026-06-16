from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from accounts.models import Profile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
        )


class UserRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True)
    re_password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=Profile.ROLE_CHOICES, default='client')

    def validate(self, data):
        if data['password'] != data['re_password']:
            raise serializers.ValidationError({'password': "Parollar mos emas!"})
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({'username': "Bu username allaqachon band!"})
        return data

    def create(self, validated_data):
        validated_data.pop('re_password')
        role = validated_data.pop('role', 'client')

        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password'],
            email=validated_data.get('email', ''),
        )
        # Profile signal orqali yaratiladi, lekin role ni yangilash kerak
        Profile.objects.filter(user=user).update(role=role)
        return user


class UserSecondRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            'username'
            'bio',
            'avatar',
            'city',
            'phone',
        )

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if not username:
            raise serializers.ValidationError({'username': 'Username kiritish majburiy!'})
        if not password:
            raise serializers.ValidationError({'password': 'Parol kiritish majburiy!'})

        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError({'non_field_errors': 'Username yoki parol noto\'g\'ri!'})
        if not user.is_active:
            raise serializers.ValidationError({'non_field_errors': 'Akkaunt faol emas!'})

        data['user'] = user
        return data
