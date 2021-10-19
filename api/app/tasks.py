from celery.decorators import task
from datetime import datetime
from .models import Notification, MaterialOrder, User
import json, asyncio
from api.settings import DOMAIN
from app.functions.functions import *


async def send_notice(notice_id):
    import websockets
    uri = "wss://" + DOMAIN + "/ws/?1"
    async with websockets.connect(uri) as ws:
         await ws.send(json.dumps({
            'data': {
                'notice_id': notice_id
            },
            'action': 'notification'
        }))

@task(name="check_materials_orders")
def check_materials_orders():
    now = datetime.now()
    material_orders = MaterialOrder.objects.filter(delivery_date_from__lte=now, delivery_date_to__gt=now, status=2)
    delivered_material_orders = MaterialOrder.objects.filter(delivery_date_to__lte=now, status=2)

    for material_order in material_orders:
        Notification.objects.filter(material_order=material_order).delete()
        user = User.objects.get(id=12)
        materials = material_order.materials.all()
        order_code = materials[0].order_item.order.code
        fabric_names = []

        for material in materials:
            fabric_names.append(material.name)

        text = "Проверьте поступление `" + "+".join(fabric_names) + "` по договору `" + order_code + "` в количестве " + str(material_order.quantity) + " " + material_order.measurement
        new_notice = Notification.objects.create(
            text=text,
            type=1,
            user=user,
            material_order=material_order
        )
        asyncio.get_event_loop().run_until_complete(update_instance('notice', 12))

    for material_order in delivered_material_orders:
        Notification.objects.filter(material_order=material_order).delete()
        user = User.objects.get(id=12)
        materials = material_order.materials.all()
        order_code = materials[0].order_item.order.code
        fabric_names = []

        for material in materials:
            fabric_names.append(material.name)

        text = "Просрочено поступление `" + "+".join(fabric_names) + "` по договору `" + order_code + "` в количестве " + str(material_order.quantity) + " " + material_order.measurement + ", измените `Ожидаемая дата поступления`"
        new_notice = Notification.objects.create(
            text=text,
            type=1,
            user=user,
            material_order=material_order
        )
        asyncio.get_event_loop().run_until_complete(update_instance('notice', 12))


