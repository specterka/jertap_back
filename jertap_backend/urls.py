"""
URL configuration for jertap_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.http import HttpResponse
from django.urls import path, include
from rest_framework.documentation import include_docs_urls

from admin_dashboard.urls import admin_dashboard_api_v1_urlpatterns
from core.urls import core_api_v1_urlpatterns
from jertap_backend import settings
from owner_dashboard.urls import owner_dashboard_api_v1_urlpatterns
from users.urls import users_api_v1_urlpatterns
from social.urls import social_api_v1_urlpatterns

def home(request):
    return HttpResponse(
        '<html><body><h1 style="text-align: center; color: #336699; margin-top: 20%;">Welcome to Jertap API </h1></body></html>')


api_v1_urlpatterns = [
    path('users/', include((users_api_v1_urlpatterns, "users"), namespace="Users V1")),
    path('core/', include((core_api_v1_urlpatterns, "core"), namespace="Core V1")),
    path('owner/', include((owner_dashboard_api_v1_urlpatterns, "owner_dashboard"), namespace="Owner V1")),
    path('super_admin/', include((admin_dashboard_api_v1_urlpatterns, "admin_dashboard"), namespace="Admin V1")),
    path('social/', include((social_api_v1_urlpatterns, "social_features"), namespace="Social V1"))
]


urlpatterns = [
    path('', home, name='index'),
    path('admin/', admin.site.urls),
    path('api/v1/', include((api_v1_urlpatterns, "v1"), namespace='v1')),
]

if settings.ENABLE_API_DOCS:
    urlpatterns += [path('api/docs/', include_docs_urls(title="Jertap API")), ]
