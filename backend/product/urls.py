from django.urls import path

from .views import (
    ProductCategoryListView,
    ProductDetailView,
    ProductHomeView,
    ProductListView,
    ServiceMessageListCreateView,
)

urlpatterns = [
    path("home/", ProductHomeView.as_view()),
    path("categories/", ProductCategoryListView.as_view()),
    path("", ProductListView.as_view()),
    path("<int:pk>/", ProductDetailView.as_view()),
    path("<int:pk>/service-messages/", ServiceMessageListCreateView.as_view()),
]
