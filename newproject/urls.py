"""newproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from newapp import views
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls) , url('^users/', include('accounts.urls')),
    url('add_village' , views.village_create),
    url('add_agbdi' , views.agbdi_create),
    url('dropdown_smo' , views.smo_dropdown),
    url('dropdown_anm' , views.anm_dropdown),
    url('dropdown_village' , views.village_dropdown),
    url('create_link_smo_anm' , views.link_smo_anm),
    url('all_dropdown' , views.all_drop_down),
    url('create_link_anm_village' , views.link_anm_village),
    url('verify_linking' , views.check_link),
    url('verify_link_icds' , views.check_link_icds),
    url('create_link_sup_village' , views.link_sup_village),
    url('create_link_village_agbdi' , views.link_village_agbdi),
    url('create_link_agbdi_worker' , views.link_agbdi_worker),
    url('icds_dropdown' , views.drop_down_icds),
    url('ping_notification' , views.check_update),
    url(('set_visit') , views.set_visit),
    url('patient_full_entry' , views.patient_data),
    url('users_record' , views.users_record),
    url('dashboard_data' , views.dashboard_data),
    url('get_h_risk_data' , views.get_high_risk_patient_data),
    url('delete_user' , views.delete_user),
    url('full_patient_data' , views.full_patient_details),
    url('get_app_data' , views.app_data),
    url('update_visit_data' , views.update_patient_data),
    url('search_record', views.search_record)


]