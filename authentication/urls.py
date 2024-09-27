from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.login_page, name="patient-login-page"),
    path('register/', views.register_page, name="register-page"),
    path('staff/', views.staff_login_page, name="staff-login-page"),


    path('register-user/', views.register_user, name="register-user"),
    
    path('combined-login/', views.combined_login, name="combined-login"),
     path('logout/', views.combined_logout, name='logout'),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)