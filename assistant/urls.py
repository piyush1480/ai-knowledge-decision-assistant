from django.urls import path
from .views import AskAssistantView,AssistantConfigView,UsageView
urlpatterns=[path('ask/',AskAssistantView.as_view()),path('assistant-config/',AssistantConfigView.as_view()),path('usage/',UsageView.as_view())]
