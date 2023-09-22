# argemerkezi/takipsistemi/urls.py
from django.urls import path
from .views import CustomLoginView
from . import views
from django.contrib import admin
from django.conf import settings
from .views import mesajlarim
from django.conf.urls.static import static
urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('login/', CustomLoginView.as_view(), name='login'),
    #path('login/', views.login_view, name='login'),  
    path('register/', views.register, name='register'),
    path('kadro/', views.kadro, name='kadro'),
    path('hakkimizda/', views.hakkimizda_view, name='hakkimizda'),
    path('tamamlanan-projeler/', views.tamamlanan_projeler, name='tamamlanan_projeler'),
    path('gizlilikpolitikasi/', views.gizlilik_politikasi, name='gizlilik_politikasi'),
    path('profil/', views.profile, name='profile'),
    path('arkadas_ekle/', views.arkadas_ekle_view, name='arkadas_ekle'),
    path('projelerim/', views.projelerim, name='projelerim'),
    path('accept_request/<int:request_id>/', views.accept_request, name='accept_request'),
    path('reject_request/<int:request_id>/', views.reject_request, name='reject_request'),
    path('mesajlarim/', mesajlarim, name='mesajlarim'),
    path('message_reply/<int:chat_id>/', views.message_reply, name='message_reply'),
    path('message_history/', views.message_history_view, name='message_history'),  
    path('start_chat/<str:recipient_username>/', views.start_chat, name='start_chat'),
    path('chat_detail/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('takvim_gorunumu/', views.takvim_gorunumu, name='takvim_gorunumu'),
    path('proje_olustur/', views.proje_olustur, name='proje_olustur'),
    path('chat_page/<int:chat_id>/', views.chat_page, name='chat_page'),
    path('logout/', views.logout_view, name='logout'),
    path('add_event/', views.add_event, name='add_event'),
    path('delete_event/<int:event_id>/', views.delete_event, name='delete_event'),
    
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)