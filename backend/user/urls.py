
from django.urls import path
from .views import RegisterView, LoginView, UserInfoView, AddressListCreateView, AddressDetailView

urlpatterns = [
	path('register/', RegisterView.as_view()),
	path('login/', LoginView.as_view()),
	path('me/', UserInfoView.as_view()),
	path('addresses/', AddressListCreateView.as_view()),
	path('addresses/<int:pk>/', AddressDetailView.as_view()),
]
