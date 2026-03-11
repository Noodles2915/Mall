from django.urls import path

from .views import (
    MerchantProductDetailManageView,
    MerchantProductListCreateView,
    MerchantProductShelfActionView,
    ProductCategoryListView,
    ProductDetailView,
    ProductHomeView,
    ProductListView,
    ServiceMessageListCreateView,
    ServiceMessageAdminListView,
    ServiceMessageAdminReplyView,
)

urlpatterns = [
    path("home/", ProductHomeView.as_view()),
    path("categories/", ProductCategoryListView.as_view()),
    path("", ProductListView.as_view()),
    path("<int:pk>/", ProductDetailView.as_view()),
    path("<int:pk>/service-messages/", ServiceMessageListCreateView.as_view()),
    path("merchant/products/", MerchantProductListCreateView.as_view()),
    path("merchant/products/<int:pk>/", MerchantProductDetailManageView.as_view()),
    path("merchant/products/<int:pk>/<str:action>/", MerchantProductShelfActionView.as_view()),
    path("admin/service-messages/", ServiceMessageAdminListView.as_view()),
    path("service-messages/<int:message_id>/reply/", ServiceMessageAdminReplyView.as_view()),
]
