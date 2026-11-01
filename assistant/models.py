from django.db import models
from core.models import Organization
class QuestionLog(models.Model):
 organization=models.ForeignKey(Organization,on_delete=models.CASCADE,related_name='questions')
 question=models.TextField()
 answered=models.BooleanField(default=False)
 created_at=models.DateTimeField(auto_now_add=True)
 decision_data=models.JSONField(default=dict,blank=True)
