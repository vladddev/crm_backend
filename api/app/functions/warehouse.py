from app.models import Consumable, Specification
from django.db.models import F
from decimal import Decimal

class Warehouse():
    item = None

    def __init__(self, item) -> None:
        self.item = item
    
    def work(self):
        specification = self.find_specification()
        self.write_off(specification, self.item.quantity)

    def find_specification(self):
        product = self.item.product.strip()
        options = map(lambda x: x.name.strip(), self.item.options.all())
        specifications = Specification.objects.filter(products__istartswith=product)
        
        for specification in specifications:
            specification_products = specification.products.split('\r\n')[1:]
            flag = True
            for specification_product in specification_products:
                if specification_product.strip() not in options:
                    flag = False

            if flag:
                return specification
        
        return None


    def write_off(self, specification, quantity = 1):
        item_leg = self.item.leg
        item_molding = self.item.molding

        if item_leg != None:
            item_leg_name = 'ножки ' + item_leg.name
            c = Consumable.objects.filter(name__iexact=item_leg_name)
            if c.exists():
                c.update(quantity=F('quantity') - (quantity * 4))
            else:
                Consumable.objects.filter(name='ножки').update(quantity=F('quantity') - (quantity * 4))

        if item_molding != None:
            item_molding_name = 'молдинг ' + item_molding.name
            c = Consumable.objects.filter(name__iexact=item_molding_name)
            if c.exists():
                c.update(quantity=F('quantity') - quantity)
            else:
                Consumable.objects.filter(name='молдинг').update(quantity=F('quantity') - quantity)
                
        if specification == None:
            return

        consumables = specification.consumables.split('\r\n')
        for consumable in consumables:
            consumable_splitted = consumable.split(' %%% ')
            if len(consumable_splitted) != 2:
                continue
            Consumable.objects.filter(name__iexact=consumable_splitted[0].strip().lower()).update(quantity=F('quantity') - (Decimal(consumable_splitted[1]) * quantity))
            
        