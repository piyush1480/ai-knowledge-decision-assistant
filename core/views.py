from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.auth.models import User
from .forms import RegisterForm
from .models import Organization
from knowledge.models import KnowledgeDocument
from assistant.models import QuestionLog

def register_view(request):
 form=RegisterForm(request.POST or None)
 if request.method=='POST' and form.is_valid():
  user=User.objects.create_user(username=form.cleaned_data['username'],email=form.cleaned_data['email'],password=form.cleaned_data['password'])
  Organization.objects.create(owner=user,name=form.cleaned_data['organization']); login(request,user); return redirect('dashboard')
 return render(request,'core/register.html',{'form':form})
def login_view(request):
 form=AuthenticationForm(request,data=request.POST or None)
 if request.method=='POST' and form.is_valid(): login(request,form.get_user()); return redirect('dashboard')
 return render(request,'core/login.html',{'form':form})
def logout_view(request): logout(request); return redirect('login')
@login_required
def dashboard(request):
 org=request.user.organization
 docs=org.documents.all(); qs=org.questions.all()
 return render(request,'core/dashboard.html',{'org':org,'docs':docs,'usage':{'total':qs.count(),'answered':qs.filter(answered=True).count(),'unanswered':qs.filter(answered=False).count()}})
@login_required
def regenerate(request):
 if request.method=='POST': request.user.organization.regenerate_token(); messages.success(request,'Assistant token regenerated.')
 return redirect('dashboard')
@xframe_options_exempt
def public_assistant(request,token):
 org=get_object_or_404(Organization,assistant_token=token)
 return render(request,'core/chat.html',{'token':org.assistant_token,'org_name':org.name})
