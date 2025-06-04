from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    
        # Blood Requests
    path('requests/', views.blood_request_list, name='blood_request_list'),
    path('requests/<int:pk>', views.view_blood_request, name='blood_request'),
    path('requests/new/', views.create_blood_request, name='blood-request-create'),
    path('requests/edit/<int:pk>/', views.update_blood_request, name='update_blood_request'),
    path('requests/delete/<int:pk>/', views.delete_blood_request, name='delete_blood_request'),
    path('requests/<int:request_id>/reject/', views.reject_blood_request, name='reject_blood_request'),
    
    # Donations
    path('donations/', views.donation_list, name='donation_list'),
    path('requests/<int:request_id>/donate/', views.create_donation, name='create_donation'),
    path('donations/edit/<int:pk>/', views.update_donation, name='update_donation'),
    path('donations/delete/<int:pk>/', views.delete_donation, name='delete_donation'),
]