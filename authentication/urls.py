from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.login_page, name="login-page"),
    path('register/', views.register_page, name="register-page"),
    path('register-user/', views.register_user, name="register-user"),
    path('login-user/', views.login_user, name="login-user"),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)