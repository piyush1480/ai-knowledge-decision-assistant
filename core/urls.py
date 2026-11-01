from django.urls import path
from . import views
urlpatterns=[path('',views.dashboard,name='dashboard'),path('register/',views.register_view,name='register'),path('login/',views.login_view,name='login'),path('logout/',views.logout_view,name='logout'),path('assistant/<str:token>/',views.public_assistant,name='public_assistant'),path('assistant/regenerate/',views.regenerate,name='regenerate')]
