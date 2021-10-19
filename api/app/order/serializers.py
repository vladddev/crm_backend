from rest_framework import serializers
from app.models import Order, OrderItem, Task, ItemOption
from app.users.serializers import UserSerializer
from app.material.serializers import MaterialSerializer, SmallMaterialSerializer


class OptionSerializer(serializers.ModelSerializer):    
    class Meta:
        model = ItemOption
        fields = '__all__'


class SmallTaskListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Task
        fields = '__all__'





class SmallOrderItemSerializer(serializers.ModelSerializer):
    materials = SmallMaterialSerializer(read_only=True, many=True)
    options = OptionSerializer(read_only=True, many=True)
    leg = serializers.StringRelatedField()
    molding = serializers.StringRelatedField()

    class Meta:
        model = OrderItem
        fields = '__all__'



class OrderSerializer(serializers.ModelSerializer):
    items = SmallOrderItemSerializer(read_only=True, many=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['responsible_user'] = UserSerializer(instance.responsible_user).data
        return ret

    class Meta:
        model = Order
        fields = '__all__'


class SmallOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class BigOrderItemSerializer(serializers.ModelSerializer):
    order = SmallOrderSerializer(read_only=True)
    tasks = SmallTaskListSerializer(many=True, read_only=True)
    materials = MaterialSerializer(read_only=True, many=True)
    options = OptionSerializer(read_only=True, many=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['completed_tasks'] = Task.objects.filter(item=instance, is_completed=True).count()
        ret['incompleted_tasks'] = Task.objects.filter(item=instance, is_completed=False).count()

        return ret

    class Meta:
        model = OrderItem
        fields = '__all__'















