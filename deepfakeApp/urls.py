
from django.urls import path,include
from deepfakeApp import views

app_name="deepfakeApp"

urlpatterns = [
   path('admin/', admin.site.urls),
    # path('',include('DeepFake.deepfakeApp.urls')),
    path('home/',views.Home,name='login'),
    path('Real/',views.check,name='Real'),
    path('Fake/',views.check,name='Fake'),
]