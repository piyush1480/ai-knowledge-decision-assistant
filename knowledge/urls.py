from django.urls import path
from .views import DocumentListUploadView,DocumentDeleteView
urlpatterns=[path('documents/',DocumentListUploadView.as_view()),path('documents/<int:pk>/',DocumentDeleteView.as_view())]
