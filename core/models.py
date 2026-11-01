import secrets
from django.db import models
from django.contrib.auth.models import User
def generate_assistant_token():
 return secrets.token_urlsafe(32)

class Organization(models.Model):
 name=models.CharField(max_length=180)
 owner=models.OneToOneField(User,on_delete=models.CASCADE,related_name='organization')
 assistant_token=models.CharField(max_length=64,unique=True,default=generate_assistant_token)
 created_at=models.DateTimeField(auto_now_add=True)
 def regenerate_token(self):
  self.assistant_token=secrets.token_urlsafe(32); self.save(update_fields=['assistant_token'])
 def __str__(self): return self.name
