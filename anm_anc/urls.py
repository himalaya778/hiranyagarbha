from django.conf.urls import url
from . import views

urlpatterns = [
url('patient_reg' , views.patient_registry),
url('patient_anc' , views.anc_visit),
]