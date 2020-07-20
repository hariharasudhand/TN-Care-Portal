from __future__ import unicode_literals

import jsonfield
from django.db import models
from users.models import Organization


class Batch(models.Model):
    batch_name = models.CharField(max_length=50, null=False, blank=False, unique=True)
    batch_code = models.BigIntegerField(null=True)
    org = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    prod_id = models.BigIntegerField()
    no_of_products = models.BigIntegerField()
    batch_date = models.DateField(auto_now_add=True)
    exp_date = models.DateField(null=True)
    release_date = models.DateField()
    status = models.CharField(max_length=10, null=False, blank=False, default='ACTIVE')
    date_added = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)
    prod_id_json = jsonfield.JSONField()

    def __str__(self):
        return self.batch_name


class Product(models.Model):
    pro_name = models.CharField(max_length=50, null=False, blank=False)
    org = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True)
    pro_price = models.BigIntegerField()
    exp_duration = models.BigIntegerField()
    status = models.CharField(max_length=10, null=False, blank=False, default='ACTIVE')
    date_added = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.pro_name


class Item(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True)
    org = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    uuid = models.CharField(max_length=100, null=True, blank=True)
    item_id = models.BigIntegerField(null=True)
    status = models.CharField(max_length=10, null=False, blank=False, default='INACTIVE')
    date_added = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.uuid
