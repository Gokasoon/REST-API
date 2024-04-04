from peewee import *

db = SqliteDatabase('db.sqlite3')

class BaseModel(Model):
    class Meta:
        database = db


class Product(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField()
    type = CharField()
    description = TextField()
    image = CharField()
    height = IntegerField()
    weight = IntegerField()
    price = FloatField()
    in_stock = BooleanField()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'image': self.image,
            'height': self.height,
            'weight': self.weight,
            'price': self.price,
            'in_stock': self.in_stock
        }
       

class OrderItem(BaseModel):
    id_OrderItem = IntegerField(primary_key=True)
    id = ForeignKeyField(Product, backref='order_items', column_name='id')  
    quantity = IntegerField()

    def to_dict(self):
        return {
            'id': self.id.id,
            'quantity': self.quantity
        }
    


class CreditCard(BaseModel):
    name = CharField()
    number = CharField()
    expiration_year = IntegerField()
    cvv = CharField(3)
    expiration_month = IntegerField()

    def to_dict(self):
        return {
            'name': self.name,
            'number': self.number,
            'expiration_year': self.expiration_year,
            'cvv': self.cvv,
            'expiration_month': self.expiration_month
        }

class Transaction(BaseModel):
    id = CharField(primary_key=True)
    success = BooleanField()
    amount_charged =FloatField()

    def to_dict(self):
        return {
            'id': self.id,
            'success': self.success,
            'amount_charged': self.amount_charged
        }
        

class ShippingInformation(BaseModel):
    country = CharField()
    address = CharField()
    postal_code = CharField()
    city = CharField()
    province = CharField()

    def to_dict(self):
        return {
            'country': self.country,
            'address': self.address,
            'postal_code': self.postal_code,
            'city': self.city,
            'province': self.province
        }
        


class Order(BaseModel):
    id = IntegerField(primary_key=True)
    total_price = FloatField()
    email = CharField(null=True)
    credit_card = ForeignKeyField(CreditCard, backref='orders', null=True)
    shipping_information = ForeignKeyField(ShippingInformation, backref='orders', null=True)
    paid = BooleanField()
    transaction = ForeignKeyField(Transaction, backref='orders', null=True)
    product = ForeignKeyField(OrderItem, backref='orders')
    shipping_price = IntegerField()

    def to_dict(self):
        return {
            'id': self.id,
            'total_price': self.total_price,
            'email': self.email,
            'credit_card': self.credit_card.to_dict() if self.credit_card is not None else {},  
            'shipping_information': self.shipping_information.to_dict() if self.shipping_information is not None else {},
            'transaction': self.transaction.to_dict() if self.transaction is not None else {},
            'paid': self.paid,
            'product': self.product.to_dict() if self.product is not None else None,  
            'shipping_price': self.shipping_price
        }


