from users import models
from .models import Notification


class AccessPermission():

    def __init__(self, roles):
        self.role = roles

    def has_prod_perm(self):
        return self.role.module.__contains__('Product')

    def has_batch_perm(self):
        return self.role.module.__contains__('Batch')

    def has_admin_perm(self):
        return self.role.module.__contains__('Admin')

    def has_billing_perm(self):
        return self.role.module.__contains__('Billing')

    def has_support_perm(self):
        return self.role.module.__contains__('Support')

    def is_create(self):
        return self.role.create

    def is_view(self):
        return self.role.view

    def is_update(self):
        return self.role.update

    def is_delete(self):
        return self.role.delete


def insert_alerts(request, module):
    if module == 'Admin':
        alert = super_user

    noti_obj = Notification.objects.all()
    noti_obj.alert_details = ''
    noti_obj.org = request.user.profile.org.id
    noti_obj.alert_to = alert