from django.urls import path
from .views import (
	AdminQualificationApplicationListView,
	AdminQualificationApplicationReviewView,
	AdminUserListView,
	AdminUserRoleUpdateView,
	AddressDetailView,
	AddressListCreateView,
	AddressSetDefaultView,
	LoginView,
	QualificationApplicationListCreateView,
	RegisterView,
	SendRegisterEmailCodeView,
	RoleListView,
	UserInfoView,
)

urlpatterns = [
	path("register/email-code/", SendRegisterEmailCodeView.as_view()),
	path("register/", RegisterView.as_view()),
	path("login/", LoginView.as_view()),
	path("me/", UserInfoView.as_view()),
	path("roles/", RoleListView.as_view()),
	path("users/", AdminUserListView.as_view()),
	path("users/<int:pk>/role/", AdminUserRoleUpdateView.as_view()),
	path("qualification-applications/", QualificationApplicationListCreateView.as_view()),
	path("admin/qualification-applications/", AdminQualificationApplicationListView.as_view()),
	path("admin/qualification-applications/<int:pk>/review/", AdminQualificationApplicationReviewView.as_view()),
	path("addresses/", AddressListCreateView.as_view()),
	path("addresses/<int:pk>/", AddressDetailView.as_view()),
	path("addresses/<int:pk>/default/", AddressSetDefaultView.as_view()),
]
