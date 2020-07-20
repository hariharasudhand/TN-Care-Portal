from django.db import models
from users.models import Organization, Groups

class Notification(models.Model):
    alert_details = models.CharField(max_length=100, default='', blank=False, null=False)
    org = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    alert_to = models.ForeignKey(Groups, on_delete=models.SET_NULL, null=True)
    uri = models.CharField(max_length=50, default='', blank=False, null=False)
    date_added = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, default='ACTIVE')

    def __str__(self):
        return self.alert_details
