from api import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, viewsets, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import BasicAuthentication
from app.models import *
from .serializers import *
import json, time
from app.functions.functions import *





class TasksListView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TaskListSerializer
        else:
            return TaskCreateSerializer

    def get_queryset(self):
        user = self.request.user
        get = self.request.query_params
        queryset = Task.objects.filter()

        if 'my' in get:
            queryset = queryset.filter(user=user)

        queryset = filter_from_get(Task, queryset, get)
        queryset = order_from_get(queryset, get)

        return queryset


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TaskListSerializer
    queryset = Task.objects.filter()


class TasksViewset(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def mass_create(self, request):
        post = request.data
        output = []

        for task in post['tasks']:
            try:
                task['deadline_from'] = time.strftime('%Y-%m-%d', time.strptime(task['deadline_from'], '%d.%m.%Y'))
            except:
                pass
            try:
                task['deadline_to'] = time.strftime('%Y-%m-%d', time.strptime(task['deadline_to'], '%d.%m.%Y'))
            except:
                pass
            try:
                task['final_datetime'] = time.strftime('%Y-%m-%d', time.strptime(task['final_datetime'], '%d.%m.%Y'))
            except:
                pass

            serializer = TaskCreateSerializer(data=task)
            if serializer.is_valid():
                serializer.save()
                
            output.append(serializer.data)

        return Response({
            'success': True,
            'result': output
        })




















