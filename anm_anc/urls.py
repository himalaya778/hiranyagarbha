from django.conf.urls import url
from . import views

urlpatterns = [
url('patient_reg' , views.patient_registry),
url('patient_anc' , views.anc_visit),
url('anm_app_with_anc' , views.anm_app_data_with_anc),
url('anm_app_without_anc' , views.anm_app_data_without_anc)
]


