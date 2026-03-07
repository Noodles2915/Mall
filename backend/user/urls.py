from django.urls import path
from .views import (
	AddressDetailView,
	AddressListCreateView,
	AddressSetDefaultView,
	LoginView,
	RegisterView,
	UserInfoView,
)

urlpatterns = [
	path("register/", RegisterView.as_view()),
	path("login/", LoginView.as_view()),
	path("me/", UserInfoView.as_view()),
	path("addresses/", AddressListCreateView.as_view()),
	path("addresses/<int:pk>/", AddressDetailView.as_view()),
	path("addresses/<int:pk>/default/", AddressSetDefaultView.as_view()),
]
