"""
URL configuration for akshaya project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from core import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('add-customer/', views.add_customer, name='add_customer'),
    path('customers/', views.customer_list, name='customer_list'),
    
    path('add-service/', views.add_service, name='add_service'),
    path('services/', views.service_list, name='service_list'),

    path('create-bill/', views.create_bill, name='create_bill'),
    path('bills/', views.bill_list, name='bill_list'),
    
    path('daily-report/', views.daily_report, name='daily_report'),
    path('invoice/<int:bill_id>/', views.invoice, name='invoice'),
    
    path('download-invoice/<int:bill_id>/', views.download_invoice_pdf, name='download_invoice'),
    
    path('monthly-report/', views.monthly_report, name='monthly_report'),
    
    path('edit-customer/<int:id>/', views.edit_customer, name='edit_customer'),
    path('delete-customer/<int:id>/', views.delete_customer, name='delete_customer'),
    
    path('edit-service/<int:id>/', views.edit_service, name='edit_service'),
    path('delete-service/<int:id>/', views.delete_service, name='delete_service'),
    
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    path('export-bills/', views.export_bills_excel, name='export_bills_excel'),
    
    path('edit-bill/<int:bill_id>/', views.edit_bill, name='edit_bill'),
    path('delete-bill/<int:bill_id>/', views.delete_bill, name='delete_bill'),
    
    path('add-bill-items/<int:bill_id>/', views.add_bill_items, name='add_bill_items'),
]
