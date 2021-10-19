from rest_framework import serializers
from app.models import Workpoint


    
class WorkpointListSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Workpoint
        fields = '__all__'