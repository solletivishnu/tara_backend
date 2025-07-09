from django.urls import path
from . import views

urlpatterns = [
    # Category and Event URLs
    path('categories/', views.category_list_create),
    path('categories/<int:pk>/', views.category_detail),

    path('events/', views.events_list_create),
    path('events/<int:pk>/', views.events_detail),

    # Document and Document Fields URLs
    path('documents/', views.document_list_create),
    path('documents/<int:pk>/', views.document_detail),

    path('document-fields/', views.document_fields_list_create),
    path('document-fields/<int:pk>/', views.document_fields_detail),
    path('document-fields-template/<int:document_id>/fields/', views.document_fields_by_document),
    path('document-fields-and-template/<int:id>')
]