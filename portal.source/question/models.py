from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    question_desc = models.CharField(max_length=200, null=False, blank=False, default='')
    answer = models.CharField(max_length=50, null=False, blank=False, default='')
    is_dependent = models.BooleanField(default=False)
    depedent_question = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, default='ACTIVE')
    date_added = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)
    add_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)