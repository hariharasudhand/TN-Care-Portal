from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from multiselectfield import MultiSelectField
from PIL import Image

MODULES = (('Admin', 'Admin'), ('Product', 'Product'), ('Billing', 'Billing'),
           ('Batch', 'Batch'), ('Support', 'Support'), ('Offer', 'Offer'))
ORG_TYPE = (('Manufacturer', 'Manufacturer'), ('SuperStockist', 'Super Stockist'),
            ('Stockist', 'Stockist'), ('Retailer', 'Retailer'))


class Organization(models.Model):
    org_name = models.CharField(max_length=50, null=False, blank=False, default='')
    address = models.CharField(max_length=250, null=True, blank=True)
    org_type = models.CharField(max_length=20, choices=ORG_TYPE, default='Retailer')
    status = models.CharField(max_length=20, null=False, blank=False, default='INACTIVE')
    date_added = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.org_name


class RolePermission(models.Model):
    role_name = models.CharField(max_length=50, default='Administrator')
    module = MultiSelectField(choices=MODULES, default='Admin')
    org = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    create = models.BooleanField(default=False)
    view = models.BooleanField(default=False)
    update = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='ACTIVE')
    date_added = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.role_name


class Groups(models.Model):
    group_name = models.CharField(max_length=25, default='Admin Group')
    org = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    role_permission = models.ForeignKey(RolePermission, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=25, default='ACTIVE')
    date_added = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.group_name


class Profile(models.Model):
    # email = models.CharField(max_length=50, null=False, blank=False, default='')
    phone = models.CharField(max_length=10, null=True, blank=True)
    photo = models.ImageField(default='male_default.png', upload_to='profile_pics')
    org = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    user_token = models.CharField(max_length=80, null=True, blank=True)
    group = models.ForeignKey(Groups, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, null=False, blank=False, default='INACTIVE')
    date_added = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)
    force_login = models.BooleanField(default=True)

    def __str__(self):
        return self.user

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.photo.path)
        if img.height > 125 or img.width > 125:
            output_size = (125, 125)
            img.thumbnail(output_size)
            img.save(self.photo.path)


# Consumer Entity
class Consumer(models.Model):
    con_name = models.CharField(max_length=50, null=False, blank=False)
    username = models.CharField(max_length=50, null=False, blank=False, unique=True)
    email = models.CharField(max_length=50, null=False, blank=False, unique=True)
    phone = models.CharField(max_length=10, null=False, blank=False, unique=True)
    password = models.CharField(max_length=100, null=False, blank=False)
    status = models.CharField(max_length=20, null=False, blank=False, default='ACTIVE')
    date_added = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.con_name


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=Organization)
def create_roles(sender, instance, created, **kwargs):
    if created:
        role = RolePermission.objects.create(org=instance)
        grp = Groups.objects.create(org=instance)
        grp.role_permission = role
        grp.save()
