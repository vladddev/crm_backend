from api import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, viewsets, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import BasicAuthentication
from app.models import *
from .serializers import *
from app.functions.functions import *
from app.pagination import *





class UsersListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    pagination_class = StandartResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.exclude(id=user.id)
        get = self.request.query_params

        # if not user.is_superuser:
        queryset = queryset.filter()

        queryset = filter_from_get(Order, queryset, get)
        queryset = order_from_get(queryset, get)

        return queryset


class UserCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    serializer_class = UserCreateSerializer



class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.filter()



class CurrentUserDetailView(generics.RetrieveUpdateAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.filter()

    def get_object(self):
        return self.request.user








