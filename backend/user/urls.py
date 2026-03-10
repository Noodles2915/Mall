from django.urls import path
from .views import (
	AdminUserListView,
	AdminUserRoleUpdateView,
	AddressDetailView,
	AddressListCreateView,
	AddressSetDefaultView,
	LoginView,
	RegisterView,
	RoleListView,
	UserInfoView,
)

urlpatterns = [
	path("register/", RegisterView.as_view()),
	path("login/", LoginView.as_view()),
	path("me/", UserInfoView.as_view()),
	path("roles/", RoleListView.as_view()),
	path("users/", AdminUserListView.as_view()),
	path("users/<int:pk>/role/", AdminUserRoleUpdateView.as_view()),
	path("addresses/", AddressListCreateView.as_view()),
	path("addresses/<int:pk>/", AddressDetailView.as_view()),
	path("addresses/<int:pk>/default/", AddressSetDefaultView.as_view()),
]
