import json, time, asyncio
from app.functions.functions import *
from datetime import date
from django.core.mail import send_mail
from django.db.models.query_utils import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import BasicAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, viewsets
from datetime import datetime, timedelta
from .serializers import *
from app.models import *
from app.pagination import *
from app.users.serializers import UserCreateSerializer
from api.settings import DOMAIN




class SystemView(viewsets.ViewSet):
    authentication_classes = []
    permission_classes = []

    def get_time(self, request):
        return Response(int(time.time()))

    def create_sp_xls(self, request):
        import xlwt

        workbook = xlwt.Workbook()
        ws = workbook.add_sheet('Specifications')

        filename = 'Расход материалов ' + str(date.today())

        get = request.query_params
        
        col_1 = ws.col(1)
        col_1.width = 256*30
        col_2 = ws.col(2)
        col_2.width = 256*30

        if 'locked' in get:
            ws.protect = True  # defaults to False
            ws.password = "admin"
            editable = xlwt.easyxf("protection: cell_locked false;")
            read_only = xlwt.easyxf("")
            filename += ' с ограничениями'
        else:
            editable = xlwt.easyxf("")
            read_only = xlwt.easyxf("")

        ws.write(0, 0, 'ID', read_only)
        ws.write(0, 1, 'Товары', read_only)
        ws.write(0, 2, 'Расходники', read_only)
        ws.write(0, 3, 'Количество', read_only)

        row_p = 1
        row_c = 1

        out = []

        for index, sp in enumerate(Specification.objects.all()):
            products = sp.products.split('\r\n')
            cons = sp.consumables.replace('.', ',').split('\r\n')

            ws.write(row_p, 0, sp.id, read_only)
            ws.write(row_p, 1, ' + '.join(products), read_only)

            for c in cons:
                # out.append([str(row_c), c])
                c_sp = c.split(' %%% ')
                ws.write(row_c, 2, c_sp[0], read_only)
                ws.write(row_c, 3, c_sp[1], editable)
                row_c += 1

            row_p = row_c

        xls_url = 'static/xls/' + filename + '.xls'
        link = "https://" + DOMAIN + "/api/" + xls_url
        workbook.save(xls_url)

        return Response(link)
    

    def create_fsp_xls(self, request):
        import xlwt

        workbook = xlwt.Workbook()
        ws = workbook.add_sheet('Fabric')

        get = request.query_params

        filename = 'Расход тканей ' + str(date.today())
        
        if 'locked' in get:
            ws.protect = True  # defaults to False
            ws.password = "admin"
            editable = xlwt.easyxf("protection: cell_locked false;")
            read_only = xlwt.easyxf("")
            filename += ' с ограничениями'
        else:
            editable = xlwt.easyxf("")
            read_only = xlwt.easyxf("")

        ws.write_merge(0, 1, 0, 0, 'ID', read_only)
        ws.write_merge(0, 1, 1, 1, 'Товар/Тип ткани', read_only)
        ws.write(0, 2, "Все в одной ткани", read_only)
        ws.write(1, 2, "Ткань 1", read_only)
        ws.write_merge(0, 0, 3, 4, "Все в одной ткани, кант в другой", read_only)
        ws.write(1, 3, "Ткань 1", read_only)
        ws.write(1, 4, "Кант", read_only)
        ws.write_merge(0, 0, 5, 6, "Подушки спинки в ткани 1, все остальное в ткани 2", read_only)
        ws.write(1, 5, "Ткань 2 + Кант", read_only)
        ws.write(1, 6, "Ткань 1", read_only)
        ws.write_merge(0, 0, 7, 8, "Подушки спинки , подушки сиденья в ткани 1, все остальное в ткани 2", read_only)
        ws.write(1, 7, "Ткань 2 + Кант", read_only)
        ws.write(1, 8, "Ткань 1", read_only)
        ws.write_merge(0, 0, 9, 10, "Сиденье+спальник +декор вставка спинки+кант везде,все остальное в ткани 2", read_only)
        ws.write(1, 9, "Ткань 2", read_only)
        ws.write(1, 10, "Ткань 1 + Кант", read_only)
        
        col_1 = ws.col(1)
        col_1.width = 256*30

        spfs = FabricSpecification.objects.filter(type=1).order_by('main_product', 'type', '-name')
        start_row = 2
        output = []


        for spf in spfs:
            name = spf.main_product.name
            
            if 'ОПТ' in name:
                continue
            
            a = []
            pks = [str(spf.main_product.pk), str(Product.objects.filter(name__iexact='ОПТ ' + name).first().pk)]
            if spf.sub_product != None:
                name = name.replace('Д/О', 'Д.к.')
            
            a.append(name)
            a.append(spf.quantity)
            ws.write(start_row, 0, '|'.join(pks), read_only)
            ws.write(start_row, 1, name, read_only)
            ws.write(start_row, 2, spf.quantity, editable)
            sub_spfs = FabricSpecification.objects.filter(main_product=spf.main_product, sub_product=spf.sub_product).exclude(type=1).order_by('type', '-name')
            col = 2
            for sub_spf in sub_spfs:
                col += 1
                a.append(str(sub_spf.type) + ' - ' + str(sub_spf.name) +  ' - ' + str(sub_spf.quantity))
                ws.write(start_row, col, sub_spf.quantity, editable)

            start_row += 1
            output.append(a)

        xls_url = 'static/xls/' + filename + '.xls'
        link = "https://" + DOMAIN + "/api/" + xls_url
        workbook.save(xls_url)

        return Response(link)


    def create_prods_xls(self, request):
        import xlwt

        workbook = xlwt.Workbook()
        ws = workbook.add_sheet('Products')

        get = request.query_params
        filename = 'Товары ' + str(date.today())

        
        if 'locked' in get:
            ws.protect = True  # defaults to False
            ws.password = "admin"
            editable = xlwt.easyxf("protection: cell_locked false;")
            read_only = xlwt.easyxf("")
            filename += ' с ограничениями'
        else:
            editable = xlwt.easyxf("")
            read_only = xlwt.easyxf("")

        col_1 = ws.col(1)
        col_1.width = 256*30

        ws.write(0, 0, "ID", read_only)
        ws.write(0, 1, "Товар", read_only)
        
        col = 2
        for i in range(400, 1800, 100):
            ws.write(0, col, "До " + str(i), read_only)
            col += 1

        ws.write(0, col, "Тип main/optional", read_only)

        row = 1
        prods = Product.objects.all().order_by('name')
        for prod in prods:
            ws.write(row, 0, prod.pk, read_only)
            ws.write(row, 1, prod.name, read_only)
            ws.write(row, 2, prod.price_before_400, editable)
            ws.write(row, 3, prod.price_before_500, editable)
            ws.write(row, 4, prod.price_before_600, editable)
            ws.write(row, 5, prod.price_before_700, editable)
            ws.write(row, 6, prod.price_before_800, editable)
            ws.write(row, 7, prod.price_before_900, editable)
            ws.write(row, 8, prod.price_before_1000, editable)
            ws.write(row, 9, prod.price_before_1100, editable)
            ws.write(row, 10, prod.price_before_1200, editable)
            ws.write(row, 11, prod.price_before_1300, editable)
            ws.write(row, 12, prod.price_before_1400, editable)
            ws.write(row, 13, prod.price_before_1500, editable)
            ws.write(row, 14, prod.price_before_1600, editable)
            ws.write(row, 15, prod.price_before_1700, editable)
            ws.write(row, 16, prod.type, editable)
            row += 1
        

        xls_url = 'static/xls/' + filename + '.xls'
        link = "https://" + DOMAIN + "/api/" + xls_url
        workbook.save(xls_url)

        return Response(link)


    def create_cons_xls(self, request):
        import xlwt

        workbook = xlwt.Workbook()
        ws = workbook.add_sheet('Products')

        get = request.query_params
        filename = 'Материалы ' + str(date.today())

        if 'locked' in get:
            ws.protect = True  # defaults to False
            ws.password = "admin"
            editable = xlwt.easyxf("protection: cell_locked false;")
            read_only = xlwt.easyxf("")
            filename += ' с ограничениями'
        else:
            editable = xlwt.easyxf("")
            read_only = xlwt.easyxf("")

        col_1 = ws.col(1)
        col_1.width = 256*20

        ws.write(0, 0, "ID", read_only)
        ws.write(0, 1, "Название", read_only)
        ws.write(0, 2, "Количество", read_only)
        ws.write(0, 3, "Единица измерения", read_only)

        cons = Consumable.objects.all()
        rownum = 1
        for c in cons:
            ws.write(rownum, 0, c.id, read_only)
            ws.write(rownum, 1, c.name, read_only)
            ws.write(rownum, 2, c.quantity, editable)
            ws.write(rownum, 3, c.unit, editable)
            rownum += 1

        xls_url = 'static/xls/' + filename + '.xls'
        link = "https://" + DOMAIN + "/api/" + xls_url
        workbook.save(xls_url)

        return Response(link)


class SpParserView(APIView):
    parser_classes = (MultiPartParser,)
    authentication_classes = []
    permission_classes = []

    def put(self, request, format=None):
        import xlrd

        file_obj = request.data['specifications']
        
        book = xlrd.open_workbook(file_contents=file_obj.read())
        sheet = book.sheet_by_index(0)

        sp_id = ''
        action = ''
        sp_prods = ''
        sp_cons = []

        for rownum in range(1, sheet.nrows):
            row = sheet.row_values(rownum)
            temp_sp_id = row[0]
            temp_sp_prods = row[1]
            # Если строка пустая, то ничего не делаем
            if temp_sp_id == '' and temp_sp_prods == '' and row[2] == '':
                    continue
                
            if rownum == sheet.nrows - 1:
                c_name = str(row[2])
                c_count = str(row[3])
                sp_cons.append(c_name + ' %%% ' + c_count)
                if action == 'create':
                    Specification.objects.create(
                        products=sp_prods,
                        consumables='\r\n'.join(sp_cons).replace(',', '.')
                    )
                elif action == 'update':
                    Specification.objects.filter(id=int(sp_id)).update(
                        products=sp_prods,
                        consumables='\r\n'.join(sp_cons).replace(',', '.')
                    )
                elif action == 'delete':
                    Specification.objects.filter(id=int(sp_id)).delete()
                    

            # Проверяем наличие либо идентификатора, либо продуктов в строке. Если есть, то смотрим action. 
            # Если есть, то у нас остались прошлые данные и мы либо обновляем спецификацию, либо создаем новую, либо удаляем
            # И обнуляем общие переменные для дальнейшей рабты с ними
            if temp_sp_id != '' or temp_sp_prods != '':
                if action == 'create':
                    Specification.objects.create(
                        products=sp_prods,
                        consumables='\r\n'.join(sp_cons).replace(',', '.')
                    )
                elif action == 'update':
                    spfs_count = len(Specification.objects.get(id=int(sp_id)).consumables.split('\r\n'))
                    new_count = len(sp_cons)
                    if spfs_count != new_count:
                        raise
                    Specification.objects.filter(id=int(sp_id)).update(
                        products=sp_prods,
                        consumables='\r\n'.join(sp_cons).replace(',', '.')
                    )
                elif action == 'delete':
                    Specification.objects.filter(id=int(sp_id)).delete()
                if action != '':
                    action = ''
                    sp_prods = ''
                    sp_cons = []
                
                c_name = str(row[2])
                c_count = str(row[3])
                sp_cons.append(c_name + ' %%% ' + c_count)

                

            # Проверяем первую строку в спецификации и определяем action 
            if temp_sp_id != '' and temp_sp_prods == '':
                sp_id = row[0]
                action = 'delete'
            elif temp_sp_id != '' and temp_sp_prods != '':
                sp_id = row[0]
                sp_prods = row[1].replace(' + ', '\r\n')
                action = 'update'
            elif temp_sp_id == '' and temp_sp_prods != '':
                sp_prods = row[1].replace(' + ', '\r\n')
                action = 'create'
            else:
                # Если пустой идентификатор и пустое имя, то мы собираем данные по расходникам 
                c_name = str(row[2])
                c_count = str(row[3])
                sp_cons.append(c_name + ' %%% ' + c_count)

        return Response()


class FSpParserView(APIView):
    parser_classes = (MultiPartParser,)
    authentication_classes = []
    permission_classes = []

    def put(self, request, format=None):
        import xlrd

        file_obj = request.data['fabric']
        
        book = xlrd.open_workbook(file_contents=file_obj.read())
        sheet = book.sheet_by_index(0)

        arr = [
            ['tk1', 1],
            ['tk1', 2],
            ['kk', 2],
            ['tk2+kk', 3],
            ['tk1', 3],
            ['tk2+kk', 4],
            ['tk1', 4],
            ['tk2', 5],
            ['tk1+kk', 5]
        ]

        for rownum in range(2, sheet.nrows):
            row = sheet.row_values(rownum)
            if row[0] == '' and row[1] == '':
                continue
            if row[0] != '' and row[1] != '':
                prod_ids = row[0].split('|')
                prod_name = row[1]
                sub_product = None
                sub_product_mass = None
                
                if 'Д.к.' in prod_name:
                    prod_name = prod_name.replace('Д.к.', 'Д/О')
                    sub_product = Product.objects.get(pk=188)
                    sub_product_mass = Product.objects.get(pk=192)

                prod_name = prod_name.strip()

                for i in range(2, 10):
                    type = arr[i - 1][1]
                    quantity = str(row[i]).strip()
                    quantity = round(float(quantity), 3)
                    FabricSpecification.objects.filter(main_product=int(prod_ids[0]), sub_product=sub_product, type=type).update(quantity=quantity)
                    FabricSpecification.objects.filter(main_product=int(prod_ids[1]), sub_product=sub_product_mass, type=type).update(quantity=quantity)
            elif row[0] == '' and row[1] != '':
                prod_ids = row[0].split('|')
                prod_name = row[1]
                sub_product = None
                sub_product_mass = None
                
                if 'Д.к.' in prod_name:
                    prod_name = prod_name.replace('Д.к.', 'Д/О')
                    sub_product = Product.objects.get(pk=188)
                    sub_product_mass = Product.objects.get(pk=192)

                prod_name = prod_name.strip()
                main_product = Product.objects.filter(name__iexact=prod_name).first() if Product.objects.filter(name__iexact=prod_name).exists() else None
                main_product_mass = Product.objects.filter(name__iexact='ОПТ ' + prod_name).first() if Product.objects.filter(name__iexact='ОПТ ' + prod_name).exists() else None

                for i in range(2, 10):
                    type = arr[i - 2][1]
                    name = arr[i - 2][0]
                    quantity = str(row[i]).strip()
                    quantity = round(float(quantity), 3)
                    # raise
                    if main_product != None:
                        FabricSpecification.objects.create(main_product=main_product, sub_product=sub_product, type=type, name=name, quantity=quantity)
                    if main_product_mass != None:
                        FabricSpecification.objects.create(main_product=main_product_mass, sub_product=sub_product_mass, type=type, name=name, quantity=quantity)
            elif row[0] != '' and row[1] == '':
                prod_ids = row[0].split('|')
                Product.objects.filter(id__in=[int(prod_ids[0]), int(prod_ids[1])]).delete()

            
            
        return Response()


class ProdsParserView(APIView):
    parser_classes = (MultiPartParser,)
    authentication_classes = []
    permission_classes = []

    def put(self, request, format=None):
        import xlrd

        file_obj = request.data['products']
        
        book = xlrd.open_workbook(file_contents=file_obj.read())
        sheet = book.sheet_by_index(0)

        for rownum in range(2, sheet.nrows):
            row = sheet.row_values(rownum)
            if row[0] == '' and row[1] == '':
                continue 
            elif row[0] != '' and row[1] != '':
                Product.objects.filter(id=int(row[0])).update(name=row[1],
                    price_before_400=row[2],
                    price_before_500=row[3],
                    price_before_600=row[4],
                    price_before_700=row[5],
                    price_before_800=row[6],
                    price_before_900=row[7],
                    price_before_1000=row[8],
                    price_before_1100=row[9],
                    price_before_1200=row[10],
                    price_before_1300=row[11],
                    price_before_1400=row[12],
                    price_before_1500=row[13],
                    price_before_1600=row[14],
                    price_before_1700=row[15],
                    type=row[16]
                )
            elif row[0] == '' and row[1] != '':
                Product.objects.create(name=row[1],
                    price_before_400=row[2],
                    price_before_500=row[3],
                    price_before_600=row[4],
                    price_before_700=row[5],
                    price_before_800=row[6],
                    price_before_900=row[7],
                    price_before_1000=row[8],
                    price_before_1100=row[9],
                    price_before_1200=row[10],
                    price_before_1300=row[11],
                    price_before_1400=row[12],
                    price_before_1500=row[13],
                    price_before_1600=row[14],
                    price_before_1700=row[15],
                    type=row[16]
                )
            elif row[0] != '' and row[1] == '':
                Product.objects.filter(pk=int(row[0])).delete()
            
        asyncio.get_event_loop().run_until_complete(update_instance('products'))
        return Response("Готово. Итого строк: " + str(sheet.nrows))


class ConsParserView(APIView):
    parser_classes = (MultiPartParser,)

    def put(self, request, format=None):
        import xlrd

        file_obj = request.data['consumables']
        
        book = xlrd.open_workbook(file_contents=file_obj.read())
        sheet = book.sheet_by_index(0)

        for rownum in range(2, sheet.nrows):
            row = sheet.row_values(rownum)
            if row[0] == '':
                if row[1] == '':
                    continue
                else:
                    Consumable.objects.create(
                        name=row[1],
                        quantity=float(row[2]),
                        unit=row[3]
                    )
            else:
                Consumable.objects.filter(id=int(row[0])).update(
                    quantity=float(row[2]),
                    unit=row[3]
                )

        return Response()


class MenuView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_menu(self, request):
        user = self.request.user
        
        response = PageSerializer(user.role.page_set.all(), context={'user': user}, many=True).data

        return Response(response)


class NotificationsView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = self.request.user

        before_60_min = datetime.now() - timedelta(minutes=60)
        Notification.objects.filter(created_datetime__lte=before_60_min, is_read=True).delete()

        queryset = Notification.objects.filter(user=user)

        output = NotificationSerializer(queryset, many=True).data
        return Response(output)

    def update(self, request):
        user = self.request.user
        post = self.request.data

        Notification.objects.filter(user=user, id__in=post['ids']).update(is_read=True)

        return Response({
            'success': True
        })

    
class PasswordResetView(viewsets.ViewSet):
    authentication_classes = []
    permission_classes = []

    def send_reset_emeil(self, request):
        post = request.data
        user = User.objects.filter(Q(email=post['username']) | Q(username=post['username'])).first()
        if user == None:
             return Response({
                'success': False,
                'message': 'Пользователь не найден'
            })

        receiver_email = user.email

        user.secret_code = str(hash(user.email + str(random.random()))**2)
        user.save()

        send_mail(
            'Восстановление пароля',
            'Чтобы восстановить пароль, перейдите по ссылке https://test.ru/sign-in?secret_key=' + str(user.secret_code),
            'security@test.ru',
            [receiver_email],
            fail_silently=False,
        )

        return Response({
            'success': True
        })

    def confirm_reset(self, request):
        post = request.data
        user = User.objects.get(secret_code=post['secret_key'])

        if user.secret_code == post['secret_key']:
            user.secret_code = ''
            user.save()
            if post['password1'] == post['password2']:
                user.set_password(post["password1"])
                user.save()
            else:
                return Response({
                    'success': False,
                    'message': 'Пароли не совпадают'
                })
        else:
            return Response({
                'success': False,
                'message': 'Неправильный код'
            })

        return Response({
            'success': True
        })


class NotificationDetailsView(generics.RetrieveDestroyAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    queryset = Notification.objects.filter()


class UserChangeQueryListView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserChangeQueryListSerializer
        else:
            return UserChangeQueryCreateSerializer

    def get_queryset(self):
        user = self.request.user
        get = self.request.query_params
        queryset = UserChangeQuery.objects.filter()

        if 'my' in get:
            queryset = queryset.filter(user=user)

        return queryset


class UserChangeQueryDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserChangeQueryListSerializer
    queryset = UserChangeQuery.objects.filter()


class SystemPostListView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = SystemPost.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SystemPostListSerializer
        else:
            return SystemPostCreateSerializer


class SystemPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = SystemPostRetrieveSerializer
    queryset = SystemPost.objects.filter()


class UserRoleListView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserRoleListSerializer
        else:
            return UserRoleCreateSerializer

    def get_queryset(self):    
        queryset = UserRole.objects.filter()

        return queryset


class UserRoleDetailView(generics.RetrieveUpdateAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserRoleListSerializer
    queryset = UserRole.objects.filter()


class PageListView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = SmallPageSerializer
