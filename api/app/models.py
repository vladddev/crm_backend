from typing import Counter
from django.db import models
from django.contrib.auth.models import AbstractUser
from .users.managers import UserManager
from PIL import Image
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.db.models import F



def system_path(instance, filepath):
    return 'uploads/system/{0}'.format(filepath)

def user_path(instance, filepath):
    return 'uploads/users/{0}/{1}'.format(instance.id, filepath)



class System(models.Model):
    pass


class SystemPost(models.Model):
    created_datetime = models.DateTimeField(auto_now_add=True, null=True)
    modified_datetime = models.DateTimeField(auto_now=True, null=True)
    removed_datetime = models.DateTimeField(blank=True, null=True)
    title = models.CharField(max_length=100, blank=False)
    excerpt = models.CharField(max_length=150, blank=True, default="")
    content = models.TextField(blank=True, default="")
    thumbnail = models.ImageField(upload_to=system_path, null=True, blank=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'


class Company(models.Model):
    created_datetime = models.DateTimeField(auto_now_add=True, null=True)
    modified_datetime = models.DateTimeField(auto_now=True, null=True)
    removed_datetime = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=False)
    payed_before = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = 'Компания'
        verbose_name_plural = 'Компании'

    def __str__(self):
        return self.name


class UserRole(models.Model):
    name = models.CharField(max_length=50, blank=True, default="")
    company = models.ForeignKey(Company, null=True, blank=True, related_name='roles', on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователей'

    def __str__(self):
        return self.name


class Page(models.Model):
    title = models.CharField(max_length=50, blank=True, default="Page")
    to = models.CharField(max_length=100, blank=True, default="/")
    icon = models.CharField(max_length=100, blank=True, default="")
    icon_alt = models.CharField(max_length=50, blank=True, null=True)
    has_childrens = models.BooleanField(default=False)

    parent = models.ForeignKey('self', null=True, blank=True, related_name='childrens', on_delete=models.SET_NULL)
    role = models.ManyToManyField(UserRole)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Страница'
        verbose_name_plural = 'Страницы'
        ordering = ['-id']
    


# class UserPermission(models.Model):
#     action = models.CharField(max_length=50, blank=True, default="")
#     role = models.ManyToManyField(UserRole)


class Workpoint(models.Model):
    prefix = models.CharField(max_length=20, blank=True, default="")
    address = models.CharField(max_length=100, blank=True, default="")
    phone_number = models.CharField(max_length=20, blank=True, default="")

    class Meta:
        verbose_name = 'Рабочая точка'
        verbose_name_plural = 'Рабочие точки'

    def __str__(self):
        return self.prefix


class User(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, default="")
    avatar = models.ImageField(upload_to=user_path, null=True, blank=True)
    position = models.CharField(max_length=50, blank=True, default="")
    middle_name = models.CharField(max_length=20, blank=True, default="")
    user_access = models.CharField(max_length=200, blank=True, default="")

    secret_code = models.CharField(max_length=200, blank=True, default="")

    created_datetime = models.DateTimeField(auto_now_add=True, null=True)
    modified_datetime = models.DateTimeField(auto_now=True, null=True)
    removed_datetime = models.DateTimeField(blank=True, null=True)

    role = models.ForeignKey(UserRole, null=True, blank=True, related_name='users', on_delete=models.SET_NULL)
    company = models.ForeignKey(Company, null=True, blank=True, related_name='users', on_delete=models.SET_NULL)
    workpoint = models.ForeignKey(Workpoint, null=True, blank=True, related_name='users', on_delete=models.SET_NULL)

    objects = UserManager()

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)

        if self.avatar:
            filepath = self.avatar.path
            width = self.avatar.width
            height = self.avatar.height

            min_size = min(width, height)

            if min_size > 300:
                image = Image.open(filepath)
                image = image.resize(
                    (round(width / min_size * 300),
                    round(height / min_size * 300)),
                    Image.ANTIALIAS
                )
                image.save(filepath)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class UserChangeQuery(models.Model):
    created_datetime = models.DateTimeField(auto_now_add=True, null=True)
    modified_datetime = models.DateTimeField(auto_now=True, null=True)
    removed_datetime = models.DateTimeField(blank=True, null=True)
    content = models.TextField(blank=True, default="")
    user = models.ForeignKey(User, null=True, blank=True, related_name='change_queries', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Запрос на редактирование пользователя'
        verbose_name_plural = 'Запросы на редактирование пользователей'

    def __str__(self):
        return self.user.username


class ChatGroup(models.Model):
    created_datetime = models.DateTimeField(auto_now_add=True, null=True)
    modified_datetime = models.DateTimeField(auto_now=True, null=True)
    removed_datetime = models.DateTimeField(blank=True, null=True)
    users = models.ManyToManyField(User)

    company = models.ForeignKey(Company, null=True, blank=True, related_name='chats', on_delete=models.CASCADE)


class ChatMessage(models.Model):
    created_datetime = models.DateTimeField(auto_now_add=True, null=True)
    modified_datetime = models.DateTimeField(auto_now=True, null=True)
    removed_datetime = models.DateTimeField(blank=True, null=True)
    content = models.TextField(blank=True, default="")

    author = models.ForeignKey(User, null=True, blank=True, related_name='messages', on_delete=models.SET_NULL)
    chat = models.ForeignKey(ChatGroup, null=True, blank=True, related_name='messages', on_delete=models.CASCADE)


class Product(models.Model):
    name = models.CharField(max_length=50, blank=True, default="")
    type = models.CharField(max_length=50, blank=True, default="main", choices=[('main', 'main'), ('optional', 'optional')])
    price_before_400 = models.IntegerField(null=True, blank=True, default=0)
    price_before_500 = models.IntegerField(null=True, blank=True, default=0)
    price_before_600 = models.IntegerField(null=True, blank=True, default=0)
    price_before_700 = models.IntegerField(null=True, blank=True, default=0)
    price_before_800 = models.IntegerField(null=True, blank=True, default=0)
    price_before_900 = models.IntegerField(null=True, blank=True, default=0)
    price_before_1000 = models.IntegerField(null=True, blank=True, default=0)
    price_before_1100 = models.IntegerField(null=True, blank=True, default=0)
    price_before_1200 = models.IntegerField(null=True, blank=True, default=0)
    price_before_1300 = models.IntegerField(null=True, blank=True, default=0)
    price_before_1400 = models.IntegerField(null=True, blank=True, default=0)
    price_before_1500 = models.IntegerField(null=True, blank=True, default=0)
    price_before_1600 = models.IntegerField(null=True, blank=True, default=0)
    price_before_1700 = models.IntegerField(null=True, blank=True, default=0)
    consumption = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name


class Leg(models.Model):
    name = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        verbose_name = 'Ножка'
        verbose_name_plural = 'Ножки'

    def __str__(self):
        return self.name


class Molding(models.Model):
    name = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        verbose_name = 'Молдинг'
        verbose_name_plural = 'Молдинги'

    def __str__(self):
        return self.name


class Order(models.Model):
    created_datetime = models.DateTimeField(auto_now_add=True, null=True)
    modified_datetime = models.DateTimeField(auto_now=True, null=True)
    removed_datetime = models.DateTimeField(blank=True, null=True)

    document = models.TextField(blank=True, default="")
    payment_method = models.SmallIntegerField(default=1, blank=True)
    sale = models.FloatField(default=0, blank=True)
    prepayment = models.FloatField(default=0, blank=True)
    payment = models.FloatField(default=0, blank=True)
    extrapayment = models.FloatField(default=0, blank=True)
    price = models.FloatField(default=0, blank=True)

    code = models.CharField(max_length=100, blank=True, default="")

    customer_full_name = models.CharField(max_length=50, blank=True, default="")
    customer_phone_number = models.CharField(max_length=20, blank=True, default="")
    customer_address = models.CharField(max_length=250, blank=True, default="")
    customer_district = models.CharField(max_length=50, blank=True, default="")

    status = models.SmallIntegerField(default=1, blank=True)
    document_link = models.CharField(max_length=200, blank=True, default="")

    delivery_date_from = models.DateField(blank=True, null=True)
    delivery_date_to = models.DateField(blank=True, null=True)
    delivery_date_real = models.DateField(blank=True, null=True)
    production_date_from = models.DateField(blank=True, null=True)
    production_date_to = models.DateField(blank=True, null=True)
    tasks_end_datetime = models.DateTimeField(blank=True, null=True)
    end_datetime = models.DateTimeField(blank=True, null=True)

    note = models.TextField(blank=True, default="")
    decline_reason = models.CharField(max_length=250, blank=True, default="")

    responsible_user = models.ForeignKey(User, null=True, blank=True, related_name='orders', on_delete=models.SET_NULL)
    company = models.ForeignKey(Company, null=True, blank=True, related_name='orders', on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return self.code


class OrderItem(models.Model):
    quantity = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=3)
    product = models.CharField(max_length=50, blank=True, default="")
    price = models.FloatField(default=0, blank=True)
    cost = models.FloatField(default=0, blank=True)
    sum = models.FloatField(default=0, blank=True)
    discount = models.FloatField(default=0, blank=True)
    schema =models.CharField(max_length=5, blank=True, default="")
    status = models.SmallIntegerField(default=1, blank=True)
    materials_type = models.SmallIntegerField(default=1, blank=True)

    note_tk1 = models.CharField(max_length=100, blank=True, default="")
    note_tk2 = models.CharField(max_length=100, blank=True, default="")
    note = models.TextField(blank=True, default="")

    leg = models.ForeignKey(Leg, null=True, blank=True, on_delete=models.SET_NULL)
    molding = models.ForeignKey(Molding, null=True, blank=True, on_delete=models.SET_NULL)
    order = models.ForeignKey(Order, null=True, blank=True, related_name='items', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказах'

    def __str__(self):
        return self.product + ' - ' + str(self.order.id)


class ItemOption(models.Model):
    quantity = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=3)
    name = models.CharField(max_length=50, blank=True, default="")
    price = models.FloatField(default=0, blank=True)
    cost = models.FloatField(default=0, blank=True)
    sum = models.FloatField(default=0, blank=True)
    discount = models.FloatField(default=0, blank=True)

    order_item = models.ForeignKey(OrderItem, null=True, blank=True, related_name='options', on_delete=models.CASCADE)
    

class MaterialOrder(models.Model):
    created_datetime = models.DateTimeField(auto_now_add=True, null=True)
    modified_datetime = models.DateTimeField(auto_now=True, null=True)
    removed_datetime = models.DateTimeField(blank=True, null=True)

    quantity = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=3)
    measurement = models.CharField(max_length=20, blank=True, default="")
    delivery_date_from = models.DateField(blank=True, null=True)
    delivery_date_to = models.DateField(blank=True, null=True)
    status = models.SmallIntegerField(default=1, blank=True)
    note = models.TextField(blank=True, default="")
    decline_reason = models.CharField(max_length=300, blank=True, default="")

    end_datetime = models.DateTimeField(blank=True, null=True)
    responsible_user = models.ForeignKey(User, null=True, blank=True, related_name='material_orders', on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Заказ ткани'
        verbose_name_plural = 'Заказы тканей'


class Material(models.Model):
    created_datetime = models.DateTimeField(auto_now_add=True, null=True)
    modified_datetime = models.DateTimeField(auto_now=True, null=True)
    removed_datetime = models.DateTimeField(blank=True, null=True)

    material = models.CharField(max_length=50, blank=True, default="")
    name = models.CharField(max_length=50, blank=True, default="")
    provider = models.CharField(max_length=50, blank=True, default="")
    price = models.FloatField(default=0, blank=True)

    order_item = models.ForeignKey(OrderItem, null=True, blank=True, related_name='materials', on_delete=models.CASCADE)
    material_order = models.ForeignKey(MaterialOrder, null=True, blank=True, related_name='materials', on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Ткань'
        verbose_name_plural = 'Ткани'
        ordering = ['created_datetime']

    def __str__(self):
        return self.material + ' ' + self.name + ' - ' + self.order_item.product 


class Consumable(models.Model):
    name = models.CharField(max_length=100, blank=True, default="")
    quantity = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=3)
    unit = models.CharField(max_length=10, blank=True, default="")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Расходный материал'
        verbose_name_plural = 'Расходные материалы'


class Task(models.Model):
    created_datetime = models.DateTimeField(auto_now_add=True, null=True)
    modified_datetime = models.DateTimeField(auto_now=True, null=True)
    removed_datetime = models.DateTimeField(blank=True, null=True)
    deadline_from = models.DateTimeField(blank=True, null=True)
    deadline_to = models.DateTimeField(blank=True, null=True)
    final_datetime = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    role = models.CharField(max_length=100, blank=True, default="")
    status = models.SmallIntegerField(default=1, blank=True)

    item = models.ForeignKey(OrderItem, null=True, blank=True, related_name='tasks', on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, related_name='tasks', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'


class OrderNumber(models.Model):
    prefix = models.CharField(max_length=20, blank=True, default="")
    counter = models.IntegerField(default=1, blank=True)

    class Meta:
        verbose_name = 'Счетчик заказов'
        verbose_name_plural = 'Счетики заказов'

    def __str__(self):
        return self.prefix + '-' + str(self.counter)


class Specification(models.Model):
    products = models.TextField(blank=True, default="", help_text="Каждое значене с новой строки")
    consumables = models.TextField(blank=True, default="", help_text="Каждое значение с новой строки в формате 'Название %%% количество'")

    class Meta:
        verbose_name = 'Спецификации'
        verbose_name_plural = 'Спецификации'
        ordering = ['products']

    def __str__(self):
        return self.products.split('\r\n')[0]


class Notification(models.Model):
    created_datetime = models.DateTimeField(auto_now_add=True, null=True)
    modified_datetime = models.DateTimeField(auto_now=True, null=True)
    removed_datetime = models.DateTimeField(blank=True, null=True)
    text = models.CharField(max_length=250, blank=True, default="")
    type = models.SmallIntegerField(default=1, choices=((1, 'Info',), (2, 'Success',),(3, 'Error',)))
    is_read = models.BooleanField(default=False)

    user = models.ForeignKey(User, null=True, blank=True, related_name='notifications', on_delete=models.CASCADE)
    material_order = models.ForeignKey(MaterialOrder, null=True, blank=True, related_name='notifications', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    def save(self, *args, **kwargs):
        if self.user != None:
            super(Notification, self).save(*args, **kwargs)


class FabricSpecification(models.Model):
    name = models.CharField(max_length=100, default='', choices=(('tk1', 'Ткань 1 ',), ('tk2', 'Ткань 2',),('kk', 'Кант',),('tk1+kk', 'Ткань 1 + Кант',),('tk2+kk', 'Ткань 2 + Кант',)))
    type = models.SmallIntegerField(default=1, blank=True)
    quantity = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=3)
    main_product = models.ForeignKey(Product, related_name='main_fspectifications', on_delete=models.CASCADE)
    sub_product = models.ForeignKey(Product, related_name='sub_fspectifications', on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = 'Спецификация тканей'
        verbose_name_plural = 'Спецификации тканей'
        ordering = ['main_product', 'type']

    def __str__(self):
        return self.name + '|' + str(self.type) + ' - ' + str(self.main_product) + ' + ' +  str(self.sub_product)


@receiver(pre_delete, sender=Order)
def update_ordernumber_hook(sender, instance, using, **kwargs):
    materials = Material.objects.filter(order_item__order=instance.id)
    for material in materials:
        MaterialOrder.objects.filter(materials=material).delete()
    code = instance.code.split('-')
    code_letters = code[0]
    try:
        code_num = code[1]
        OrderNumber.objects.filter(prefix=code_letters, counter=int(code_num)).update(counter=F('counter') - 1)
    except:
        pass