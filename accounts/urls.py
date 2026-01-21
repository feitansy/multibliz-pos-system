from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Account settings
    path('settings/', views.account_settings, name='account_settings'),
    path('settings/edit/', views.edit_profile, name='edit_profile'),
    path('settings/security/', views.security_dashboard, name='security_dashboard'),
    path('settings/users/', views.user_management, name='user_management'),
    path('settings/users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('settings/users/role/<int:user_id>/', views.update_user_role, name='update_user_role'),
    path('change-password/', views.change_password, name='change_password'),
]
