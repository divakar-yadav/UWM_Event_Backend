"""srpc_new URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, include


urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/signup/', include('signup.urls')),
    path('api/signin/', include('signin.urls')),
    path('api/home/', include('home.urls')),
    path('api/precheckposter/', include('precheckposter.urls')),
    path('api/insertgrade/', include('insertgrade.urls')),
    path('api/explearning/', include('explearning.urls')),
    path('api/three-mt/', include('threemt.urls')),
    path("api/", include("index.urls")),
    path('api/spa-283771828/', include('admindashboard.urls'))
]
