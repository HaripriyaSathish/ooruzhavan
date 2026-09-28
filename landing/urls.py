from django.urls import path

from . import views

app_name = 'landing'

urlpatterns = [
    path('', views.index, name='index'),
    path('enquiry/', views.submit_enquiry, name='submit_enquiry'),
]
