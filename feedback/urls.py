from django.urls import path

from . import views

app_name = 'feedback'

urlpatterns = [
    path('create/', views.create_feedback, name='create'),
]
