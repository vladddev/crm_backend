from rest_framework import serializers
from app.models import User, Company
from django.contrib.auth.hashers import make_password





class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username', 'email', 'first_name', 'last_name', 'middle_name', 'phone_number', 'avatar', 'position', 'user_access', 'workpoint')


class UserCreateSerializer(serializers.ModelSerializer):    
    def validate_password(self, value: str) -> str:
        return make_password(value)
        
    class Meta:
        model = User
        fields = ('username', 'password', 'role')


















