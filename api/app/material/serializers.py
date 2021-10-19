from rest_framework import serializers
from app.models import MaterialOrder, Material, OrderItem, Order, ItemOption

class OptionSerializer(serializers.ModelSerializer):    
    class Meta:
        model = ItemOption
        fields = '__all__'

        
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    options = OptionSerializer(read_only=True, many=True)

    class Meta:
        model = OrderItem
        fields = '__all__'





class SmallMaterialSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Material
        fields = '__all__'


class MaterialSerializer(serializers.ModelSerializer):
    order_item = OrderItemSerializer(read_only=True)

    class Meta:
        model = Material
        fields = '__all__'


class MaterialOrderSerializer(serializers.ModelSerializer):
    materials = MaterialSerializer(read_only=True, many=True)
    responsible_user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = MaterialOrder
        fields = '__all__'




















