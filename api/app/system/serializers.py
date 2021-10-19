from rest_framework import serializers
from app.models import *
from app.users.serializers import UserSerializer






class SmallPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = '__all__'


class PageSerializer(serializers.ModelSerializer):
    childrens = serializers.SerializerMethodField() 

    def get_childrens(self, obj):
        user = self.context.get('user')
        
        if obj.has_childrens:
            return SmallPageSerializer(user.role.page_set.filter(parent_page=obj.id), many=True).data
        else:
            return None

    class Meta:
        model = Page
        fields = '__all__'



class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class UserChangeQueryListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserChangeQuery
        fields = '__all__'


class UserChangeQueryCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = UserChangeQuery
        fields = '__all__'


class SystemPostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemPost
        exclude = ('content', )

class SystemPostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemPost
        fields = '__all__'

class SystemPostRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemPost
        exclude = ('excerpt', )


class UserRoleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = '__all__'

class UserRoleListSerializer(serializers.ModelSerializer):
    page_set = SmallPageSerializer(many=True, read_only=True)

    class Meta:
        model = UserRole
        fields = '__all__'















