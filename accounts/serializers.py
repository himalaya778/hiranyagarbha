from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    #email = serializers.EmailField(
    #        required=True,
    #        validators=[UniqueValidator(queryset=User.objects.all())]
    #        )
    username = serializers.CharField(max_length=32,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    password = serializers.CharField(min_length=8,write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password')

    def create(self, validated_data):
        print(validated_data)
        user = User.objects.create_user(validated_data['username'],
             password = validated_data['password'] )

        #user = super(UserSerializer, self).create(validated_data)
        return user

class AuthCustomTokenSerializer(serializers.Serializer):
    email_or_username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        email_or_username = attrs.get('email_or_username')
        password = attrs.get('password')

        #if email_or_username and password:
        #    # Check if user sent email
        #    if validate_email(email_or_username):
        #        user_request = get_object_or_404(
        #            User,
        #            email=email_or_username,
        #        )

         #       email_or_username = user_request.username
        print(email_or_username, " " , password)
        user = authenticate(username=email_or_username, password=password)
        print("authenticated")
        #print(user)
            
        if user:
            if not user.is_active:
                msg = ('User account is disabled.')
                raise ValidationError(msg)
        else:
            msg = ('Unable to log in with provided credentials.')
            raise ValidationError(msg)
        #else:
        #    msg = ('Must include "email or username" and "password"')
        #    raise ValidationError(msg)

        attrs['user'] = user
        
        return attrs


