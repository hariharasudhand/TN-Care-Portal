from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from users import views as user_view
from app import views

urlpatterns = [
    # Matches any html file - to be used for gentella
    # Avoid using your .html in your resources.
    # Or create a separate django app.
    re_path(r'^.*\.html', views.gentella_html, name='gentella'),

    # The home page
    path('', auth_views.LoginView.as_view(template_name='users/login.html'), name='index'),
    # path('', views.index, name='index'),
    path('', views.success, name='success'),
    path('home/', views.success, name='home'),
]

