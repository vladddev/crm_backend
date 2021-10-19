from app.models import FabricSpecification, MaterialOrder, ItemOption, Product




class Fabric():
    types = [
            ['tk1'],
            ['tk1', 'kk'],
            ['tk1', 'tk2+kk'],
            ['tk1', 'tk2+kk'],
            ['tk1+kk', 'tk2']
        ]
    
    def __init__(self, item) -> None:
        self.item = item

    def work(self):
        materials_type = self.item.materials_type
        user = self.item.order.responsible_user
        types = self.types[materials_type - 1]
        
        for type in types:
            name = self.item.product
            filter = {
                'name': type,
                'main_product': Product.objects.filter(name=name).first().pk,
                'type': materials_type
            }
            if ItemOption.objects.filter(order_item=self.item.pk, name__iexact="Спальное место").exists():
                filter['sub_product'] = 188
            if ItemOption.objects.filter(order_item=self.item.pk, name__iexact="ОПТ Спальное место").exists():
                filter['sub_product'] = 192

            fs = FabricSpecification.objects.filter(**filter)
            if not fs.exists():
                continue

            fs = fs.first()
            splitted_materials = type.replace('tk1', 'Ткань 1').replace('tk2', 'Ткань 2').replace('kk', 'Кант').split('+')

            new_mat_order = MaterialOrder.objects.create(quantity=fs.quantity * self.item.quantity, measurement='м.', note=self.item.note, delivery_date_from=self.item.order.production_date_from, delivery_date_to=self.item.order.production_date_to, responsible_user=user)
            
            for mat in splitted_materials:
                self.item.materials.filter(material=mat).update(material_order=new_mat_order)

                

