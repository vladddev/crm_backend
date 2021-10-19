from rest_framework import serializers
from app.models import Task
from app.users.serializers import UserSerializer
from app.order.serializers import BigOrderItemSerializer






class TaskListSerializer(serializers.ModelSerializer):
    item = BigOrderItemSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = '__all__'


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

















