"""DeepFake URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path,include
from deepfakeApp import views

app_name="deepfakeApp"
urlpatterns = [
    path('admin/', admin.site.urls),
    # path('',include('DeepFake.deepfakeApp.urls')),
    path('',views.HomePage,name='login'),
    path('Real/',views.Real,name='Real'),
    path('Fake/',views.Fake,name='Fake'),
    path('check/',views.check,name='check'),
]
