from django import forms
from django.contrib.auth.models import User
class RegisterForm(forms.Form):
 organization=forms.CharField(max_length=180)
 username=forms.CharField(max_length=150)
 email=forms.EmailField()
 password=forms.CharField(widget=forms.PasswordInput,min_length=8)
 def clean_username(self):
  value=self.cleaned_data['username']
  if User.objects.filter(username=value).exists(): raise forms.ValidationError('Username already exists.')
  return value
