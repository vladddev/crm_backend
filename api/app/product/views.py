from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import BasicAuthentication
from rest_framework.response import Response
from rest_framework import generics, viewsets
from .serializers import *
from app.models import *
from app.pagination import *
from app. functions.functions import remove_spaces


class ProductView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_price(self, request):
        get = request.query_params
        product_id = get['product_id']
        material_price = str(int(get['material_price']) + 99)

        if int(get['material_price']) < 400:
            material_price = "400"
        elif int(get['material_price']) > 1700:
            material_price = "1700"

        product = None
        price_k = None
        output = None

        try:
            product = Product.objects.get(id=product_id)
        except:
            return Response({
                'message': 'Некорректное название'
            })

        price_k = material_price[0:-2]

        price_k = 4 if int(material_price) < 400 else price_k
        price_k = 17 if int(material_price) > 1700 else price_k


        try:
            output = getattr(product, 'price_before_' + price_k + '00')
        except:
            return Response({
                'message': 'Некорректная цена'
            })

        return Response({
            'price': output
        })

    def modify_consumables(self, request):
        post = request.data

        for cons in post['consumables']:
            Consumable.objects.filter(pk=cons['id']).update(quantity=cons['quantity'])

        return Response({
            'success': True
        })

    def load_consumables(self, request):
        import xlrd

        file = request.FILES.get('materials')
        book = xlrd.open_workbook(file_contents=file.read())
        sheet = book.sheet_by_index(0)

        added = 0
        updated = 0

        for rownum in range(0, sheet.nrows):
            row = sheet.row_values(rownum)
            name = remove_spaces(row[0])
            if name == '':
                continue 
            
            if Consumable.objects.filter(name=name).exists():
                Consumable.objects.filter(name=name).update(unit=row[1].strip(), quantity=float(row[2]))
                updated += 1
            else:
                Consumable.objects.create(name=name, unit=row[1].strip(), quantity=float(row[2]))
                added += 1

        return Response({
            'success': True,
            'updated': updated,
            'added': added
        })


class ProductsListView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProductsListSerializer

    def get_queryset(self):
        queryset = Product.objects.filter()
        if 'type' in self.request.query_params:
            queryset = queryset.filter(type=self.request.query_params['type'])
        return queryset


class LegsListView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = LegsListSerializer
    queryset = Leg.objects.all()


class MoldingListView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MoldingListSerializer
    queryset = Molding.objects.all()


class ConsumableListView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ConsumableListSerializer
    queryset = Consumable.objects.all()


