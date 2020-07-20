from django.urls import path
from . import views

urlpatterns = [

    # add product links
    path('product/', views.product, name='product'),
    path('update_product/<int:id>/', views.update_product, name='update_product'),
    path('product/<int:id>/delete/', views.cancel_product, name='delete_product'),
    path('view_product/<int:id>/', views.view_product, name='view_product'),

    # batch links
    path('batch/', views.batch, name='batch'),
    path('view_batch/<int:id>/', views.view_batch, name='view_batch'),

    # item links
    path('item/<int:id>/', views.item, name='item'),
    path('view_qr_code/<int:id>/', views.view_qr_code, name='view_qr_code'),
]
