from django.urls import path
from .views import test_vies

urlpatterns = [
    path('', test_vies, name="base")
]