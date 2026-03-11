from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import HomeBanner, Product, ProductCategory, ServiceMessage
from .serializers import (
    HomeBannerSerializer,
    ProductCategorySerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    MerchantProductCreateUpdateSerializer,
    MerchantProductDetailSerializer,
    ServiceMessageSerializer,
)


def is_admin_or_merchant(user):
    return bool(user.is_authenticated and (user.is_admin_role or user.is_merchant_role))


def can_manage_product(user, product):
    if user.is_admin_role:
        return True
    return user.is_merchant_role and product.merchant_id == user.id


class ProductHomeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        banners = HomeBanner.objects.filter(is_active=True)
        hot_products = Product.objects.filter(is_active=True, is_hot=True).select_related("category")[:8]

        return Response(
            {
                "code": 0,
                "message": "ok",
                "data": {
                    "banners": HomeBannerSerializer(banners, many=True).data,
                    "hot_products": ProductListSerializer(hot_products, many=True).data,
                },
            }
        )


class ProductCategoryListView(generics.ListAPIView):
    serializer_class = ProductCategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ProductCategory.objects.filter(is_active=True)

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response({"code": 0, "message": "ok", "data": serializer.data})


class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related("category")
        request = self.request
        drf_request = request if isinstance(request, Request) else None

        keyword = (drf_request.query_params.get("keyword", "") if drf_request else "").strip()
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword)
                | Q(subtitle__icontains=keyword)
                | Q(description__icontains=keyword)
            )

        category = drf_request.query_params.get("category") if drf_request else None
        if category and category.isdigit():
            category_id = int(category)
            child_ids = list(
                ProductCategory.objects.filter(parent_id=category_id, is_active=True).values_list("id", flat=True)
            )
            queryset = queryset.filter(category_id__in=[category_id, *child_ids])

        is_hot = drf_request.query_params.get("is_hot", "") if drf_request else ""
        if is_hot.lower() in {"1", "true", "yes"}:
            queryset = queryset.filter(is_hot=True)

        return queryset

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response({"code": 0, "message": "ok", "data": serializer.data})


class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    queryset = Product.objects.filter(is_active=True).select_related("category").prefetch_related("images")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        payload = self.get_serializer(instance).data
        payload["customer_service_entry"] = f"/api/products/{instance.id}/service-messages/"
        return Response({"code": 0, "message": "ok", "data": payload})


class ServiceMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = ServiceMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_product(self):
        return generics.get_object_or_404(Product.objects.filter(is_active=True), pk=self.kwargs["pk"])

    def get_queryset(self):
        product = self.get_product()
        return ServiceMessage.objects.filter(product=product, user=self.request.user).select_related("user")

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response({"code": 0, "message": "ok", "data": serializer.data})

    def create(self, request, *args, **kwargs):
        product = self.get_product()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save(user=request.user, product=product)
        return Response(
            {"code": 0, "message": "ok", "data": self.get_serializer(message).data},
            status=status.HTTP_201_CREATED,
        )


class MerchantProductListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_admin_or_merchant(request.user):
            return Response({"code": 1003, "message": "权限不足"}, status=status.HTTP_403_FORBIDDEN)

        queryset = Product.objects.select_related("category").order_by("-id")
        if request.user.is_merchant_role:
            queryset = queryset.filter(merchant=request.user)

        serializer = MerchantProductDetailSerializer(queryset, many=True)
        return Response({"code": 0, "message": "ok", "data": serializer.data})

    def post(self, request):
        if not is_admin_or_merchant(request.user):
            return Response({"code": 1003, "message": "权限不足"}, status=status.HTTP_403_FORBIDDEN)

        serializer = MerchantProductCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        merchant = request.user if request.user.is_merchant_role else None
        product = serializer.save(merchant=merchant)
        return Response(
            {"code": 0, "message": "ok", "data": MerchantProductDetailSerializer(product).data},
            status=status.HTTP_201_CREATED,
        )


class MerchantProductDetailManageView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return generics.get_object_or_404(Product.objects.select_related("category"), pk=pk)

    def get(self, request, pk):
        product = self.get_object(pk)
        if not can_manage_product(request.user, product):
            return Response({"code": 1003, "message": "权限不足"}, status=status.HTTP_403_FORBIDDEN)
        return Response({"code": 0, "message": "ok", "data": MerchantProductDetailSerializer(product).data})

    def put(self, request, pk):
        product = self.get_object(pk)
        if not can_manage_product(request.user, product):
            return Response({"code": 1003, "message": "权限不足"}, status=status.HTTP_403_FORBIDDEN)

        serializer = MerchantProductCreateUpdateSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"code": 0, "message": "ok", "data": MerchantProductDetailSerializer(product).data})

    def patch(self, request, pk):
        product = self.get_object(pk)
        if not can_manage_product(request.user, product):
            return Response({"code": 1003, "message": "权限不足"}, status=status.HTTP_403_FORBIDDEN)

        serializer = MerchantProductCreateUpdateSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"code": 0, "message": "ok", "data": MerchantProductDetailSerializer(product).data})

    def delete(self, request, pk):
        product = self.get_object(pk)
        if not can_manage_product(request.user, product):
            return Response({"code": 1003, "message": "权限不足"}, status=status.HTTP_403_FORBIDDEN)

        product.delete()
        return Response({"code": 0, "message": "ok"}, status=status.HTTP_200_OK)
