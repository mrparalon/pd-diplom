from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from backend.models import Shop, Category, Product, ProductInfo, Parameter,\
                           ProductParameter


@shared_task
def send_email(title, message, email):
    title = str(title)
    message = str(message)
    msg = EmailMultiAlternatives(
        # title:
        title,
        # message:
        message,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        email
    )
    msg.send()
    return f'Title: {msg.subject}, Message:{msg.body}'

@shared_task
def import_shop_data(data, user_id):
    shop, _ = Shop.objects.get_or_create(name=data['shop'], user_id=user_id)
    category_list_created = []
    for category in data['categories']:
        category_object, created = Category.objects.\
                                   get_or_create(id=category['id'],
                                                 name=category['name'])
        category_object.shops.add(shop.id)
        if created:
            category_list_created.append(category_object)
        else:
            category_object.save()
    if category_list_created:
        Category.objects.bulk_create(category_list_created)

    ProductInfo.objects.filter(shop_id=shop.id).delete()
    for item in data['goods']:
        product, _ = Product.objects.get_or_create(name=item['name'],
                                                   category_id=item['category'])

        product_info = ProductInfo.objects.create(product_id=product.id,
                                                  external_id=item['id'],
                                                  model=item['model'],
                                                  price=item['price'],
                                                  price_rrc=item['price_rrc'],
                                                  quantity=item['quantity'],
                                                  shop_id=shop.id)
        for name, value in item['parameters'].items():
            parameter_object, _ = Parameter.objects.get_or_create(name=name)
            ProductParameter.objects.create(product_info_id=product_info.id,
                                            parameter_id=parameter_object.id,
                                            value=value)