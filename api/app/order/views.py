from api import settings
from django.db.models import F
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import BasicAuthentication
from app.models import *
from .serializers import *
import json, time, asyncio
from datetime import datetime, timedelta
from app.functions.functions import *
from app.functions.warehouse import Warehouse
from app.functions.fabric import Fabric
from app.functions.pdf import PDF
from app.pagination import *







class OrderView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_next_code(self, request):
        user = request.user

        workshop_prefix = user.workpoint.prefix if user.workpoint != None else 'XXX'
        order_code = ''
        counter = 1
        prefix_queryset = OrderNumber.objects.filter(prefix=workshop_prefix)

        if prefix_queryset.exists():
            counter = prefix_queryset.last().counter
            counter += 1
        
        order_code = workshop_prefix + '-' + str(counter)

        return Response({
            "code": order_code
        })

    
    def create_document(self, request):
        import locale, urllib.parse
        locale.setlocale(category=locale.LC_ALL, locale="Russian")

        order_id = request.query_params['order_id']
        order = None

        try:
            order = Order.objects.get(id=order_id)
        except:
            return Response({
                "message": "Неправильный номер заказа"
            })

        if order.document_link != '':
            return Response({
                "link": order.document_link
            })

        resp_user = order.responsible_user
        workpoint_phone = resp_user.workpoint.phone_number if resp_user.workpoint != None else ''

        pdf = PDF()
        pdf.add_page()
        pdf.add_font('DejaVu', '', 'static/fonts/DejaVuSansCondensed.ttf', uni=True)
        pdf.set_auto_page_break(auto=True, margin=10)

        # шапка

        pdf.set_font("DejaVu", size=9)
        pdf.cell(50, 12, txt="«Goldera Home»", align="C")
        pdf.cell(70)
        pdf.cell(35, 10, txt="Номер телефона")
        pdf.cell(35, 10, txt=workpoint_phone, align="C")
        pdf.ln(6)
        pdf.set_font('DejaVu', size=7)
        pdf.cell(60, 8, txt="мягкая мебель для дома и офиса", align="C")
        pdf.ln(4)

        pdf.cell(80)
        pdf.set_font('DejaVu', size=9)
        pdf.cell(20, 11, txt="ДОГОВОР №")
        pdf.cell(30, 11, txt=order.code)
        pdf.cell(10)
        pdf.cell(10, 10, txt="от")
        pdf.cell(35, 10, txt=order.created_datetime.strftime('%d.%m.%Y'), align="C")

        # блок товара
        for index, item in enumerate(order.items.all()):
            summ = item.sum

            pdf.set_font('DejaVu', size=8)
            pdf.ln(10)
            pdf.cell(10, 5, txt="№", border=1, align="C")
            pdf.cell(80, 5, txt="Наименование комплекта мебели", border=1, align="C")
            pdf.cell(15, 5, txt="Кол-во", border=1, align="C")
            pdf.cell(30, 5, txt="Цена (руб.)", border=1, align="C")
            pdf.cell(25, 5, txt="Скидка (%)", border=1, align="C")
            pdf.cell(30, 5, txt="Сумма (руб.)", border=1, align="C")
            pdf.ln(5)
            
            pdf.cell(10, 5, txt="1", border=1, align="C")
            pdf.cell(80, 5, txt=item.product, border=1, align="C")
            pdf.cell(15, 5, txt=str(item.quantity), border=1, align="C")
            pdf.cell(30, 5, txt=str(item.cost), border=1, align="C")
            pdf.cell(25, 5, txt=str(item.discount), border=1, align="C")
            pdf.cell(30, 5, txt=str(item.sum), border=1, align="C")
            pdf.ln(5)

            for i, option in enumerate(item.options.all()):
                summ += option.sum

                pdf.cell(10, 5, txt=str(i+2), border=1, align="C")
                pdf.cell(80, 5, txt=option.name, border=1, align="C")
                pdf.cell(15, 5, txt=str(option.quantity), border=1, align="C")
                pdf.cell(30, 5, txt=str(option.cost), border=1, align="C")
                pdf.cell(25, 5, txt=str(option.discount), border=1, align="C")
                pdf.cell(30, 5, txt=str(option.sum), border=1, align="C")
                pdf.ln(5)

            pdf.cell(135)
            pdf.cell(55, 5, txt="  Итого: " + str(summ), border=1)

            materials = item.materials.all()

            pdf.ln(8)
            pdf.cell(100, 5, txt="КОМПЛЕКТАЦИЯ:", border=1, align="C")
            pdf.cell(60, 5, txt="Поставщик:", border=1, align="C")
            pdf.cell(30, 5, txt="Цена:", border=1, align="C")
            pdf.ln(5)
            pdf.cell(30, 5, txt="Ткань 1: ", border=1, align="C")
            pdf.cell(70, 5, txt=materials[0].name, border=1)
            pdf.cell(60, 5, txt=materials[0].provider, border=1, align="C")
            pdf.cell(30, 5, txt=str(materials[0].price), border=1, align="C")
            pdf.ln(5)
            pdf.cell(30, 5, txt="Ткань 2: ", border=1, align="C")
            pdf.cell(70, 5, txt=materials[1].name, border=1)
            pdf.cell(60, 5, txt=materials[1].provider, border=1, align="C")
            pdf.cell(30, 5, txt=str(materials[1].price), border=1, align="C")
            pdf.ln(5)
            pdf.cell(30, 5, txt="Кант: ", border=1, align="C")
            pdf.cell(70, 5, txt=materials[2].name, border=1)
            pdf.cell(60, 5, txt=materials[2].provider, border=1, align="C")
            pdf.cell(30, 5, txt=str(materials[2].price), border=1, align="C")

            pdf.ln(8)
            pdf.rect(10, pdf.get_y(), 20, 15)
            pdf.cell(20, 10, txt="Схема:", align="C")
            pdf.cell(10)
            pdf.cell(20, 5, txt="Ножки:", border=1)
            pdf.cell(40, 5, txt=item.leg.name if item.leg else "", border=1)
            pdf.ln(5)
            pdf.cell(20, 10, txt=item.schema, align="C")
            pdf.cell(10)
            pdf.cell(20, 5, txt="Молдинг:", border=1)
            pdf.cell(40, 5, txt=item.molding.name if item.molding else "", border=1)
            pdf.ln(8)
            pdf.cell(30)
            pdf.cell(160, 5, txt="  ПРИМЕЧАНИЕ:", border=1)
            pdf.ln(5)
            pdf.cell(30)
            pdf.cell(20, 5, txt="ТК1:", border=1, align="C")
            pdf.cell(140, 5, txt=item.note_tk1, border=1)
            pdf.ln(5)
            pdf.cell(30)
            pdf.cell(20, 5, txt="ТК2:", border=1, align="C")
            pdf.cell(140, 5, txt=item.note_tk2, border=1)
            pdf.ln(5)
            pdf.multi_cell(190, 4, txt=item.note, border=1)

        # подвал
        pdf.set_font('DejaVu', size=9)
        pdf.ln(5)
        y = pdf.get_y()
        pdf.cell(190, 7, txt="  ИТОГО К ОПЛАТЕ: " + str(order.price), border=1)

        payment_methods = [
            'Наличный расчет',
            'Терминал',
            'Перевод по счету',
            'Перевод по реквизитам'
        ]

        pdf.ln(10)
        pdf.cell(103, 7, txt="  Получено при оформлении (" + payment_methods[order.payment_method - 1] + "): " + str(order.prepayment), border=1)
        pdf.cell(4)

        tm = timedelta(days=14)
        created = order.created_datetime
        final_payment_date = created + tm
        pdf.cell(83, 7, txt="  Окончательный платёж (" + final_payment_date.strftime('%d.%m.%Y') + "): " + str(order.payment), border=1)
        
        pdf.ln(10)
        y = pdf.get_y() + 7
        pdf.rect(10, pdf.get_y(), 190, 18)
        pdf.cell(30, 10, txt="  Покупатель: Ф.И.О.")
        pdf.line(50, y, 190, y)
        pdf.cell(10)
        pdf.cell(30, 7, txt=order.customer_full_name)
        pdf.ln(7)
        pdf.cell(25, 7, txt="  Адрес, телефон")
        pdf.line(43, y+7, 190, y+7)
        pdf.cell(7)
        pdf.set_font('DejaVu', size=7)
        pdf.cell(22, 7, txt=order.customer_address + ', ' + order.customer_phone_number)
        pdf.set_font('DejaVu', size=9)

        pdf.ln(15)
        pdf.cell(40, 7, txt="Дата изготовления:",  align="C", border=1)
        pdf.cell(40, 7, txt="Дата доставки:",  align="C", border=1)
        pdf.cell(110, 7, txt="  Район доставки:", border=1)
        pdf.ln()
        if order.production_date_from == order.production_date_to:
            pdf.cell(40, 7, txt=order.production_date_from.strftime('%d.%m.%Y'),  align="C", border=1)
        else:
            pdf.cell(40, 7, txt=order.production_date_from.strftime('%d.%m.%Y') + '-' + order.production_date_to.strftime('%d.%m.%Y'),  align="C", border=1)
        if order.delivery_date_from == order.delivery_date_to:
            pdf.cell(40, 7, txt=order.delivery_date_from.strftime('%d.%m.%Y'),  align="C", border=1)
        else:
            pdf.cell(40, 7, txt=order.delivery_date_from.strftime('%d.%m.%Y') + '-' + order.delivery_date_to.strftime('%d.%m.%Y'),  align="C", border=1)
        pdf.cell(70, 7, txt="  С габаритами мебели ознакомлен(а):", border=1)
        pdf.multi_cell(40, 3.5, txt="  Покупатель \n  (подпись):", border=1)

        if pdf.get_y() > 220:
            pdf.add_page()
        r_user = order.responsible_user
        pdf.set_font('DejaVu', size=9)
        pdf.cell(190, 20, txt="Ответственность распространяется только на обязательства, оформленные в письменном виде.")
        pdf.ln(15)
        pdf.cell(80, 7, txt="  Заказ оформил: " + r_user.first_name + ' ' + r_user.last_name, border=1)
        pdf.cell(20)
        pdf.multi_cell(90, 3.5, txt="С правилами эксплуатации, ухода и безопасного \nиспользования мягкой мебели ознакомлен (а):")

        pdf.ln(5)
        pdf.cell(100)
        pdf.multi_cell(80, 4, txt="  Покупатель \n  (Ф.И.О., подпись):", border=1)

        if order.code.find('Опт') < 0:
            pdf.add_page()
            pdf.image('doc1.jpg', x=0, y=0, w=200, h=290)
            pdf.set_font('DejaVu', size=8)
            pdf.ln(10)
            pdf.cell(140)
            pdf.cell(50, txt=order.created_datetime.strftime('«%d» %B %Y г.'))
            pdf.ln(9)
            pdf.cell(8)
            pdf.cell(200, txt=order.customer_full_name)
            pdf.add_page()
            pdf.image('doc2.jpg', x=0, y=0, w=200, h=290)
            pdf.add_page()
            pdf.image('doc3.jpg', x=0, y=0, w=200, h=290)

        pdf_url = "static/orders/" + order.code + ".pdf"
        pdf.output(pdf_url)

        link = "https://" + settings.DOMAIN + "/api/" + pdf_url.replace('\\', "%5C")

        order.document_link = link
        order.save()


        return Response({
            "link": link
        })


class ItemsListView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = BigOrderItemSerializer
    pagination_class = StandartResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        get = self.request.query_params
        queryset = OrderItem.objects.all()

        queryset = filter_from_get(OrderItem, queryset, get)
        queryset = order_from_get(queryset, get)

        if 'with_materials' in get:
            new_queryset = []
            for item in queryset:
                order = item.order
                if MaterialOrder.objects.filter(materials__order_item=item).count() == MaterialOrder.objects.filter(materials__order_item=item, status__gt=2).count():
                    new_queryset.append(item)
            queryset = new_queryset

        return queryset


class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = BigOrderItemSerializer
    queryset = OrderItem.objects.filter()

    def perform_update(self, serializer):
        serializer.save()
        
        item = self.get_object()
        order = item.order
        if OrderItem.objects.filter(order=order).count() == OrderItem.objects.filter(order=order, status=3).count():
            if order.status == 3:
                order.status = 4
                order.tasks_end_datetime = datetime.now()
                order.delivery_date_real = datetime.now()
                order.save()
        

class OrdersListView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    pagination_class = StandartResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        get = self.request.query_params
        queryset = Order.objects.filter(company=user.company)

        queryset = filter_from_get(Order, queryset, get)
        queryset = order_from_get(queryset, get)

        return queryset

    def perform_create(self, serializer):
        import copy

        user = self.request.user
        post = self.request.data
        order_data = post['order']
        workshop_prefix = user.workpoint.prefix if user.workpoint != None else 'XXX'
        order_code = ''
        counter = 1
        if 'code' in order_data and order_data['code'] != '':
            order_code = order_data['code']
        else:
            if OrderNumber.objects.filter(prefix=workshop_prefix).exists():
                counter = OrderNumber.objects.filter(prefix=workshop_prefix).last().counter
                counter += 1

            order_code = workshop_prefix + '-' + str(counter)
        
        order_data['code'] = order_code
        order_data['responsible_user'] = user
        order_data['company'] = user.company
        items = post['items']

        if 'delivery_date_from' in order_data:
            order_data['delivery_date_from'] = time.strftime('%Y-%m-%d', time.strptime(order_data['delivery_date_from'], '%d.%m.%Y'))
        if 'delivery_date_to' in order_data:
            order_data['delivery_date_to'] = time.strftime('%Y-%m-%d', time.strptime(order_data['delivery_date_to'], '%d.%m.%Y'))
        if 'delivery_date_real' in order_data:
            order_data['delivery_date_real'] = time.strftime('%Y-%m-%d', time.strptime(order_data['delivery_date_real'], '%d.%m.%Y'))
        if 'production_date_from' in order_data:
            order_data['production_date_from'] = time.strftime('%Y-%m-%d', time.strptime(order_data['production_date_from'], '%d.%m.%Y'))
        if 'production_date_to' in order_data:
            order_data['production_date_to'] = time.strftime('%Y-%m-%d', time.strptime(order_data['production_date_to'], '%d.%m.%Y'))

        new_order = serializer.save(**order_data)

        if 'code' not in order_data or order_data['code'] != '':
            if OrderNumber.objects.filter(prefix=workshop_prefix).exists():
                OrderNumber.objects.filter(prefix=workshop_prefix).update(counter=counter)
            else:
                OrderNumber.objects.create(prefix=workshop_prefix, counter=counter)

        if len(items) > 0:
            for item in items:
                options = copy.deepcopy(item['options'])
                materials = copy.deepcopy(item['materials'])

                del item['options']
                del item['materials']

                item['leg'] = Leg.objects.get(id=item['leg']) if item['leg'] else None
                item['molding'] = Molding.objects.get(id=item['molding']) if item['molding'] else None

                new_item = OrderItem.objects.create(order=new_order, **item)

                if len(options) > 0:
                    for option in options:
                        ItemOption.objects.create(order_item=new_item, **option)

                if len(materials) > 0:
                    for material in materials:
                        Material.objects.create(order_item=new_item, **material)

        asyncio.get_event_loop().run_until_complete(update_instance('order'))


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Order.objects.filter()

    def perform_update(self, serializer):
        order = self.get_object()
        post = self.request.data
        order_data = dict(post)

        if 'delivery_date_from' in order_data:
            order_data['delivery_date_from'] = time.strftime('%Y-%m-%d', time.strptime(order_data['delivery_date_from'], '%d.%m.%Y'))
        if 'delivery_date_to' in order_data:
            order_data['delivery_date_to'] = time.strftime('%Y-%m-%d', time.strptime(order_data['delivery_date_to'], '%d.%m.%Y'))
        if 'production_date_from' in order_data:
            order_data['production_date_from'] = time.strftime('%Y-%m-%d', time.strptime(order_data['production_date_from'], '%d.%m.%Y'))
        if 'production_date_to' in order_data:
            order_data['production_date_to'] = time.strftime('%Y-%m-%d', time.strptime(order_data['production_date_to'], '%d.%m.%Y'))
        if 'end_datetime' in order_data:
            order_data['end_datetime'] = time.strftime('%Y-%m-%d', time.strptime(order_data['end_datetime'], '%d.%m.%Y'))

        if 'items' in order_data:
            for item in order_data['items']:
                item_data = dict(item)
                if 'materials' in item_data:
                    for material in item_data['materials']:
                        Material.objects.filter(pk=material['id']).update(**material)

                    del item_data['materials']

                if 'options' in item_data:
                    for option in item_data['options']:
                        ItemOption.objects.filter(pk=option['id']).update(**option)
                
                    del item_data['options']

                OrderItem.objects.filter(pk=item_data['id']).update(**item_data)

            del order_data['items']

        serializer.save(**order_data)
        if 'status' in order_data and order_data['status'] == 3:
            for item in order.items.all():
                wh = Warehouse(item)
                wh.work()

                f = Fabric(item)
                f.work()
            asyncio.get_event_loop().run_until_complete(update_instance('order'))
            asyncio.get_event_loop().run_until_complete(update_instance('materials'))


class GuestOrderDetailView(generics.RetrieveAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = OrderSerializer
    queryset = Order.objects.filter()






















