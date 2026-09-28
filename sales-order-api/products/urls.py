from django.urls import path
from .views import ProductListCreateView, ProductDetailsView

urlpatterns = [
    path('', ProductListCreateView.as_view(), name='prodct-list-create'),
    path('<int:pk>/', ProductDetailsView.as_view(), name='product-detail')
]
