from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('miniature/<slug:slug>/', views.miniature_detail, name='miniature_detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 