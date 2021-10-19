from rest_framework import serializers
from app.models import Product, Leg, Molding, Consumable



class ProductsListSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Product
        fields = ('id', 'name', 'price_before_1700')

    
class LegsListSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Leg
        fields = '__all__'


class MoldingListSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Molding
        fields = '__all__'


class ConsumableListSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Consumable
        fields = '__all__'