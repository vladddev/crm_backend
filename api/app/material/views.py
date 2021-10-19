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
import time



class MaterialView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_pair(self, request):
        get = request.query_params
        outputs = [
            [
                'Все в одной ткани',
                ''
            ],
            [
                'Все в одной',
                'Кант'
            ],
            [
                'Подушки спинки',
                'Все остальное'
            ],
            [
                'Подушки спинки, подушки сидения',
                'Все остальное'
            ],
            [
                'Сиденье, спальник, декоративная вставка спинки, кант',
                'Все остальное'
            ]
        ]
        return Response(outputs[int(get['type']) - 1])


class MaterialOrdersListView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MaterialOrderSerializer
    pagination_class = StandartResultsSetPagination

    def get_queryset(self):
        get = self.request.query_params
        queryset = MaterialOrder.objects.filter()

        queryset = filter_from_get(MaterialOrder, queryset, get)
        queryset = order_from_get(queryset, get)

        return queryset

    
    def perform_create(self, serializer):
        user = self.request.user
        company = self.request.user.company
        post = self.request.data
        order_item = OrderItem.objects.filter(order=int(post['order']), product=post['product_name']).first()

        delivery_date_from = time.strftime('%Y-%m-%d', time.strptime(post['delivery_date_from'], '%d.%m.%Y'))
        delivery_date_to = time.strftime('%Y-%m-%d', time.strptime(post['delivery_date_to'], '%d.%m.%Y'))
        
        new_material_order = MaterialOrder.objects.create(quantity=post['quantity'], measurement='м.', status=2, note=post['note'], delivery_date_from=delivery_date_from, delivery_date_to=delivery_date_to, responsible_user=user)
        Material.objects.create(order_item=order_item, material=post['material'], name=post['name'], provider=post['provider'], material_order=new_material_order)


class MaterialOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MaterialOrderSerializer
    queryset = MaterialOrder.objects.filter()

    def perform_update(self, serializer):
        post = self.request.data
        material_data = dict(post)

        if 'delivery_date_from' in post:
            material_data['delivery_date_from'] = time.strftime('%Y-%m-%d', time.strptime(material_data['delivery_date_from'], '%d.%m.%Y'))
        if 'delivery_date_to' in post:
            material_data['delivery_date_to'] = time.strftime('%Y-%m-%d', time.strptime(material_data['delivery_date_to'], '%d.%m.%Y'))
        if 'end_datetime' in post:
            material_data['end_datetime'] = time.strftime('%Y-%m-%d', time.strptime(material_data['end_datetime'], '%d.%m.%Y'))
        serializer.save(**material_data)





















