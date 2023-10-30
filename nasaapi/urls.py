from django.urls import path
from nasaapi.views import index


urlpatterns = [
    path('', index),
]
