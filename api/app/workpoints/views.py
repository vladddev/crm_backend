from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import BasicAuthentication
from rest_framework.response import Response
from rest_framework import generics, viewsets
from datetime import datetime, timedelta
from .serializers import *
from app.models import *


class WorkpointsListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = WorkpointListSerializer
    queryset = Workpoint.objects.all()