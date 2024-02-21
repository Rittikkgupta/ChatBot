


from django.urls import path
from login.views import *


urlpatterns = [
    path('DialogflowWebhook/', DialogflowWebhook.as_view(), name='DialogflowWebhook'),
    
]
