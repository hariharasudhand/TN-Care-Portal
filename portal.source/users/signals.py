from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, Organization, RolePermission, Groups

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