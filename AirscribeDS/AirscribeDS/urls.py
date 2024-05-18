"""
URL configuration for AirscribeDS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing,name='landing'),
    path('Login', views.logins,name='Login'),
    path('user_status/<int:id>', views.user_status,name='user_status'),
    path('logout',views.logout,name='logout'),

    path('admin_home/', views.admin_home,name='admin_home'),
    path('change_password', views.change_password,name='change_password'),
    path('verify_users', views.verify_users,name='verify_users'),
    path('view_users', views.view_users,name='view_users'),
    path('view_review', views.view_review,name='view_review'),
    path('view_login_details',views.view_login_details,name='view_login_details'),
    
    path('user_home', views.user_home,name='user_home'),
    path('user_registeration', views.user_registeration,name='user_registeration'),
    path('view_profile', views.view_profile,name='view_profile'),
    path('edit_profile/<int:id>', views.edit_profile,name='edit_profile'),
    path('rating', views.rating,name='rating'),
    path('user_view_review', views.user_view_review,name='user_view_review'),
    path('changepassword_user', views.changepassword_user,name='changepassword_user'),
    path('air_scribe', views.air_scribe,name='air_scribe'),
    
]
