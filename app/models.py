from peewee import *

conn = SqliteDatabase("./db.sqlite")


class BaseModel(Model):
    class Meta:
        database = conn


class User(BaseModel):
    id = AutoField()  # уникальный идентификатор
    email = CharField()
    username = CharField()
    password = CharField()
    is_superuser = BooleanField()


class Category(BaseModel):
    id = AutoField()
    name = CharField()


class Product(BaseModel):
    id = AutoField()  # Уникальный идентификатор
    name = CharField()
    description = TextField()
    price = IntegerField()
    photo_url = CharField(null=True)  # Поле для хранения ссылки на фото
    category = ForeignKeyField(Category, backref="products")


class Order(BaseModel):
    id = AutoField()  # уникальный идентификатор
    ordered_by = ForeignKeyField(User, backref="orders", null=True)
    product = ForeignKeyField(Product, backref="orders")
    amount = IntegerField()


conn.create_tables([User, Product, Order, Category])

"""categories = [
    "Акустические гитары",
    "Классические гитары",
    "Электрические гитары",
    "Аксессуары",
]

for category in categories:
    category_ = Category(name=category)
    category_.save()
"""