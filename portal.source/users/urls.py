from django.urls import path
from django.contrib.auth import views as auth_views
from . import views as user_view


urlpatterns = [

    path('register/', user_view.register, name='register'),
    path('profile/', user_view.profile, name='profile'),
    path('profile/<int:id>/update', user_view.profile_update, name='profile-update'),
    path('profile/<int:id>/delete', user_view.profile_delete, name='profile-delete'),


    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('success/', user_view.login_request, name='success'),
    path('logout/', auth_views.LogoutView.as_view(template_name='app/index.html'), name='logout'),

    # Password reset links (ref: https://github.com/django/django/blob/master/django/contrib/auth/views.py)
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'),
         name='password_change_done'),

    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='users/password_change.html'),
         name='password_change'),

    path('password_reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),

    # organization links
    path('org-onboard/', user_view.org_onboard, name='org-onboard'),
    path('org-registered/', user_view.org_registered, name='org-registered'),
    path('org-update/', user_view.org_update, name='org-update'),
    path('org-approve/<int:id>', user_view.org_approve, name='org-approve'),
    path('org-approved/', user_view.org_approved, name='org-approved'),

    # Roles links
    path('roles/', user_view.roles_add, name='roles'),
    path('roles/<int:id>/update', user_view.roles_update, name='roles-update'),
    path('roles/<int:id>/delete/', user_view.roles_cancel, name='roles-delete'),

    # Groups links
    path('groups/', user_view.group_add, name='groups'),
    path('groups/<int:id>/update', user_view.group_update, name='groups-update'),
    path('groups/<int:id>/delete/', user_view.groups_cancel, name='groups-delete'),


]