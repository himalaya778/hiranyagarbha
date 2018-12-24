from django.conf.urls import url
from . import views

urlpatterns = [
url('visit_data' , views.smo_anc_visit),
url('delivery_details' , views.delivery_details),
url('pnc_data', views.pnc_visit),
url('42_pnc', views.final_visit)
]