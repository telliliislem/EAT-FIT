from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_or_edit_business, name='create_business'),
    path("order/<int:order_id>/done/", views.mark_order_done, name="mark_order_done"),
    path("order/<int:order_id>/delete/", views.delete_order, name="delete_order"),
]
