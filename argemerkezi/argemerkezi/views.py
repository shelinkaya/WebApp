# argemerkezi/views.py:
import random
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from takipsistemi.models import UserProfile, Project, Assignment
from django.contrib.auth import authenticate, login as auth_login
from takipsistemi.forms import LoginForm  
from django.core.files.storage import FileSystemStorage  
from django.http import JsonResponse
from django.views.generic import TemplateView
from takipsistemi.forms import NotForm
from takipsistemi.models import Note
from takipsistemi.models import FriendshipRequest
from django.db.models import Q
from datetime import datetime, timedelta
from takipsistemi.forms import ArkadasEkleForm, NotForm, EventForm
from django.contrib.auth.decorators import login_required
from takipsistemi.models import FriendshipRequest, Message, Etkinlik
from takipsistemi.forms import MessageForm, EtkinlikForm
import logging
from takipsistemi.models import Chat
logger = logging.getLogger(__name__)
from django.core.exceptions import PermissionDenied
from takipsistemi.models import Proje
from takipsistemi.forms import ProjeForm
from takipsistemi.models import GanttSema  

def kadro(request):
    return render(request, 'kadro.html')

def index(request):
    return render(request, 'index.html')

def hakkimizda_view(request):
    return render(request, 'hakkimizda.html')

def tamamlanan_projeler(request):
    return render(request, 'tamamlanan_projeler.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from takipsistemi.models import UserProfile

def register(request):
    if request.method == 'POST':
        # Diğer form verilerini alın
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password_repeat = request.POST['password_repeat']
        birth_date = request.POST['birth_date']
        gender = request.POST['gender']
        contact_info = request.POST['contact_info']
        occupation = request.POST['occupation']
        expertise = request.POST['expertise']
        bio = request.POST['bio']
        accept_terms = request.POST.get('accept_terms')

        if password != password_repeat:
            messages.error(request, 'Şifreler uyuşmuyor.')
        elif not accept_terms:
            messages.error(request, 'Koşulları ve gizlilik politikasını kabul etmelisiniz.')
        elif not email.endswith('@allalci.com'):
            messages.error(request, 'Sadece @allalci.com uzantılı e-posta adresleri kabul edilmektedir.')
        else:
            try:
                # Şifreleri güvenli bir şekilde sakla
                hashed_password = make_password(password)
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=hashed_password,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # UserProfile modeline kaydet
                user_profile = UserProfile.objects.create(
                    user=user,
                    name=f"{first_name} {last_name}",
                    birth_date=birth_date,
                    gender=gender,
                    contact_info=contact_info,
                    occupation=occupation,
                    expertise=expertise,
                    bio=bio
                )

                messages.success(request, 'Kaydınız başarıyla oluşturuldu. Giriş yapabilirsiniz.')
                return redirect('register')
            except Exception as e:
                messages.error(request, 'Kayıt işlemi sırasında bir hata oluştu. Lütfen daha sonra tekrar deneyin.')

    return render(request, 'register.html')


def gizlilik_politikasi(request):
    return render(request, 'gizlilikpolitikasi.html')

from django.contrib.auth import authenticate, login

from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
logger = logging.getLogger(__name__)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                return redirect('profile')
            else:
                messages.error(request, 'Giriş bilgileri geçersiz.')
        else:
            messages.error(request, 'Form geçersiz. Lütfen giriş bilgilerinizi kontrol edin.')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('index')  # Çıkış yapıldıktan sonra ana sayfaya yönlendir




def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    redirect_to = request.GET.get('redirect_to', None)
    if redirect_to == 'calendar':
        return redirect('calendar') 

    return render(request, 'profil.html', {'user_profile': user_profile})

def accept_request(request, request_id):
    friend_request = get_object_or_404(FriendshipRequest, id=request_id, to_user=request.user, is_accepted=False)
    friend_request.is_accepted = True
    friend_request.save()
    return redirect('arkadas_ekle')

def reject_request(request, request_id):
    friend_request = get_object_or_404(FriendshipRequest, id=request_id, to_user=request.user, is_accepted=False)
    friend_request.delete()
    return redirect('arkadas_ekle')

def arkadas_ekle_view(request):
    incoming_friend_requests = FriendshipRequest.objects.filter(to_user=request.user, is_accepted=False)
    outgoing_friend_requests = FriendshipRequest.objects.filter(from_user=request.user)
    
    accepted_requests_from_me = FriendshipRequest.objects.filter(from_user=request.user, is_accepted=True)
    accepted_requests_to_me = FriendshipRequest.objects.filter(to_user=request.user, is_accepted=True)
    
    my_friends = set()
    for accepted_request in accepted_requests_from_me:
        my_friends.add(accepted_request.to_user)
    for accepted_request in accepted_requests_to_me:
        my_friends.add(accepted_request.from_user)
    
    if request.method == 'POST':
        form = ArkadasEkleForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username_or_email']
            try:
                user = User.objects.get(Q(username=username_or_email) | Q(email=username_or_email))
                if user != request.user:
                    FriendshipRequest.objects.create(from_user=request.user, to_user=user)
                    messages.success(request, f'{user.username} kullanıcısına arkadaşlık isteği gönderildi.')
                else:
                    messages.error(request, 'Kendi kendinize arkadaşlık isteği gönderemezsiniz.')
            except User.DoesNotExist:
                messages.error(request, 'Kullanıcı bulunamadı.')
        
        return redirect('arkadas_ekle')
    else:
        form = ArkadasEkleForm()
    
    context = {
        'incoming_friend_requests': incoming_friend_requests,
        'outgoing_friend_requests': outgoing_friend_requests,
        'my_friends': my_friends,
        'form': form,
    }
    
    return render(request, 'arkadas_ekle.html', context)

def mesajlarim(request):
    # Arkadaşlarınızı ve mesajlarınızı almak için gerekli kodları ekleyin
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            recipient_username = form.cleaned_data['recipient']
            content = form.cleaned_data['content']
            media_file = form.cleaned_data['media_file']
            sender = request.user  # Gönderen, giriş yapmış kullanıcıdır.
            
            # İşte burada yeni bir mesaj oluşturun
            message = form.save_message(sender)

            # Yeni bir sohbet sayfası oluşturmak için mesajın olduğu sayfaya yönlendirin
            if message:
                return redirect('chat_page', chat_id=message.chat.id)
            else:
                messages.error(request, 'Mesaj gönderilemedi.')

    else:
        form = MessageForm(request=request)

    context = {
        # Gerekli bağlam verilerini ekleyin
        'form': form,
    }

    return render(request, 'mesajlarim.html', context)

def chat_page(request, chat_id):
    chat = Chat.objects.get(id=chat_id)
    messages = Message.objects.filter(chat=chat)

    return render(request, 'chat_page.html', {'chat': chat, 'messages': messages})

def message_reply(request, chat_id):
    print("Chat ID:", chat_id)
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            content = form.cleaned_data['content']
            media_file = form.cleaned_data['media_file']
            logger.debug("content: %s", content)
            logger.debug("media_file: %s", media_file)

            # chat_id'yi form verilerinden alın
            chat_id = chat_id

            try:
                selected_chat = Message.objects.get(id=chat_id)
                
                # Mesajın alıcı ve gönderen rollerini değiştirerek yanıt mesajı oluşturun
                Message.objects.create(sender=request.user, recipient=selected_chat.sender, content=content, media_file=media_file)

                messages.success(request, 'Mesajınız gönderildi.')
            except Message.DoesNotExist:
                messages.error(request, 'Mesaj bulunamadı.')

            return redirect('mesajlarim')

def proje_olustur(request):
    if request.method == 'POST':
        form = ProjeForm(request.POST)
        if form.is_valid():
            proje = form.save(commit=False)
            # Proje verilerini kaydedin
            proje.save()

            # Formdan başlangıç ve bitiş tarihlerini alın
            baslangic_tarihi = form.cleaned_data['baslangic_tarihi']
            bitis_tarihi = form.cleaned_data['bitis_tarihi']

            # Başlangıç ve bitiş tarihlerine göre Gantt verilerini oluşturun
            gantt_data = [
                # Gantt şemasına eklemek istediğiniz görevleri ve zaman çizelgesi verilerini buraya ekleyin
                # Örnek: { id: 1, text: "Görev 1", start_date: baslangic_tarihi, duration: 5 },
            ]

            return render(request, 'gantt_sayfasi.html', {'gantt_data': gantt_data})
    else:
        form = ProjeForm()
    return render(request, 'proje_olustur.html', {'form': form})

def projelerim(request):
    projeler = Proje.objects.all()  # Tüm projeleri al
    return render(request, 'projelerim.html', {'projeler': projeler})

def message_history_view(request):
    # Örnek bir veri modeli oluşturuyoruz. Gerçek verileri burada kullanabilirsiniz.
    message_history_data = [
        {'sender': 'User1', 'content': 'Message 1', 'timestamp': '2023-08-31 12:00:00'},
        {'sender': 'User2', 'content': 'Message 2', 'timestamp': '2023-08-31 12:30:00'},
        # ... Diğer mesajlar ...
    ]
    
    context = {
        'message_history_data': message_history_data,
    }
    
    return render(request, 'message_history.html', context)

def start_chat(request, recipient_username):
    recipient = get_object_or_404(User, username=recipient_username)
    
    # Kontrol edin: Eğer zaten böyle bir sohbet varsa, o sohbete yönlendirin.
    chat = Chat.objects.filter(participants=request.user).filter(participants=recipient)
    if chat.exists():
        return redirect('chat_detail', chat_id=chat.first().id)
    
    # Yeni bir sohbet oluşturun
    new_chat = Chat.objects.create()
    new_chat.participants.add(request.user, recipient)
    
    return redirect('chat_detail', chat_id=new_chat.id)

from django.shortcuts import render, redirect, get_object_or_404
from takipsistemi.models import Etkinlik
from takipsistemi.forms import EtkinlikForm

def takvim_gorunumu(request):
    etkinlikler = Etkinlik.objects.all()
    form = EtkinlikForm()

    return render(request, 'takvim_gorunumu.html', {'etkinlikler': etkinlikler, 'form': form})

def add_event(request):
    if request.method == 'POST':
        form = EtkinlikForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('takvim_gorunumu')
    else:
        form = EtkinlikForm()
    return render(request, 'takvim_gorunumu.html', {'form': form})

def delete_event(request, event_id):
    if request.method == 'DELETE':
        try:
            etkinlik = Etkinlik.objects.get(pk=event_id)
            etkinlik.delete()
            return JsonResponse({'success': True})
        except Etkinlik.DoesNotExist:
            return JsonResponse({'success': False})
    return JsonResponse({'success': False})



def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    participants = chat.participants.all()
    
    if request.user not in participants:
        raise PermissionDenied
    
    messages = Message.objects.filter(
        Q(sender=request.user, recipient=participants[0]) |  # Filtreleme seninle veya alıcıyla olabilir
        Q(sender=participants[0], recipient=request.user)     # Filtreleme alıcıyla veya seninle olabilir
    ).order_by('timestamp')
    
    context = {
        'chat': chat,
        'messages': messages,
    }
    
    return render(request, 'chat_detail.html', context)