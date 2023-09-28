# argemerkezi/takipsistemi/views.py
import random
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile, Project, Assignment
from django.contrib.auth import authenticate, login as auth_login
from .forms import LoginForm
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views.generic import TemplateView
from .models import Note
from .models import Event
from datetime import datetime, timedelta
from django.db.models import Q
from .forms import ArkadasEkleForm, NotForm, EventForm
from django.contrib.auth.decorators import login_required
from .forms import MessageForm, EtkinlikForm
from .models import FriendshipRequest, Message, Etkinlik
import logging
from .models import Chat
from django.core.exceptions import PermissionDenied
from .models import Proje
from .forms import ProjeForm
from .models import GanttSema  # GanttSema modelini ekleyin
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout
from django.http import HttpResponse
logger = logging.getLogger(__name__)
def kadro(request):
    return render(request, 'kadro.html')

def index(request):
    return render(request, 'index.html')

def hakkimizda_view(request):
    return render(request, 'hakkimizda.html')

def tamamlanan_projeler(request):
    return render(request, 'tamamlanan_projeler.html')

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

def logout_view(request):
    logout(request)
    return redirect('index')  # Çıkış yapıldıktan sonra ana sayfaya yönlendir

def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    redirect_to = request.GET.get('redirect_to', None)
    if redirect_to == 'calendar':
        return redirect('calendar') 

    return render(request, 'profil.html', {'user_profile': user_profile})

    friend_request = get_object_or_404(FriendshipRequest, id=request_id, to_user=request.user, is_accepted=False)
    
    # Arkadaşlık isteğini reddetme işlemi (isteği silme)
    friend_request.delete()
    
    return redirect('arkadas_ekle')  # İstenilen sayfaya yönlendirme yapabilirsiniz

from django.db import transaction

def assign_project(user_profile, project, adam_ay):
    # Bu işlemi bir işlem (transaction) içinde yapmak için kullanılır.
    with transaction.atomic():
        # 1. Kullanıcının toplam adam/ay oranını güncelle
        user_profile.total_adam_ay -= adam_ay
        user_profile.save()

        # 2. Proje atamasını oluştur
        assignment = Assignment.objects.create(project=project, assigned_to=user_profile, allocation=adam_ay)

        # 3. Projenin toplam adam/ay oranını güncelle
        project.total_adam_ay += adam_ay
        project.save()

        return assignment

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
@login_required
def mesajlarim(request):
    # Kullanıcının arkadaşlarını alın
    my_friends = request.user.userprofile.friends.all()

    # Kullanıcının sohbetlerini alın
    chats = Chat.objects.filter(participants=request.user)

    # Mesaj gönderme formunu işleyin
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            content = form.cleaned_data['content']
            media_file = form.cleaned_data['media_file']

            # Gönderen ve alıcı arasında sohbeti al veya oluştur
            chat, created = Chat.objects.get_or_create(participants=request.user)
            if not created:
                other_user = form.cleaned_data['recipient']
                chat.participants.add(other_user)

            # Mesajı oluştur
            message = Message.objects.create(chat=chat, sender=request.user, content=content, media_file=media_file)

            return redirect('chat_page', chat_id=message.chat.id)

    else:
        form = MessageForm()

    # Kullanıcının aldığı mesajları alın
    messages = Message.objects.filter(chat__participants=request.user).order_by('-timestamp')

    return render(request, 'mesajlarim.html', {
        'my_friends': my_friends,
        'form': form,
        'chats': chats,
        'messages': messages,
    })

def message_reply(request, chat_id):
    # Burada mesaj yanıtı görüntüleme işlemleri gerçekleştirilebilir
    return HttpResponse(f'Mesaj yanıtı görüntüleme sayfası, chat_id: {chat_id}')
@login_required
def chat_page(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in chat.participants.all():
        return redirect('mesajlarim')

    messages = Message.objects.filter(chat=chat).order_by('timestamp')
    form = MessageForm()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.chat = chat
            message.save()
            form = MessageForm()

    return render(request, 'chat_page.html', {'chat': chat, 'messages': messages, 'form': form})

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

from django.shortcuts import render
from .models import Proje, GanttSema

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Proje



from django.shortcuts import render, redirect
from .forms import ProjeForm
from .models import UserProfile


from django.http import HttpResponse
from .models import UserProfile
@login_required
def proje_olustur(request):
    if request.method == 'POST':
        form = ProjeForm(request.POST)
        if form.is_valid():
            # Diğer proje bilgilerini kaydedin
            proje = form.save(commit=False)

            # Projede çalışacak kişileri alın
            calisacak_kisiler = []
            total_adam_ay = 0.0

            for i in range(1, 15):  # İhtiyaca göre kişi sayısını ayarlayın
                username = request.POST.get(f'username_{i}')
                adam_ay_orani = request.POST.get(f'adam_ay_orani_{i}')

                if username and adam_ay_orani:
                    adam_ay_orani = float(adam_ay_orani)

                    # Kullanıcının mevcut adam/ay oranını alın
                    try:
                        user_profile = UserProfile.objects.get(user__username=username)
                        mevcut_adam_ay = user_profile.adam_ay_orani
                    except UserProfile.DoesNotExist:
                        mevcut_adam_ay = 0.0

                    # Yeterli adam/ay oranı kalmadıysa hata mesajı gösterin
                    if mevcut_adam_ay < adam_ay_orani:
                        form.add_error(None, f"{username} için yetersiz adam/ay oranı.")
                        return render(request, 'proje_olustur.html', {'form': form})

                    calisacak_kisiler.append({'username': username, 'adam_ay_orani': adam_ay_orani})
                    total_adam_ay += adam_ay_orani

            # Projede çalışacak kişilerin adam/ay oranlarını güncelleyin
            for calisan in calisacak_kisiler:
                username = calisan['username']
                adam_ay_orani = calisan['adam_ay_orani']
                user_profile = UserProfile.objects.get(user__username=username)
                user_profile.adam_ay_orani -= adam_ay_orani
                user_profile.save()

            # Proje toplam adam/ay oranını güncelleyin
            proje.total_adam_ay = total_adam_ay
            proje.save()

            # Kullanıcının adam/ay oranını güncelleyin
            current_user_profile = UserProfile.objects.get(user=request.user)
            current_user_profile.adam_ay_orani -= total_adam_ay
            current_user_profile.save()

            return render(request, 'gantt_sayfasi.html')
    else:
        form = ProjeForm()

    context = {
        'form': form,
    }
    return render(request, 'proje_olustur.html', context)









    


from django.shortcuts import render, redirect
from .models import Project, UserProfile, Assignment

from django.db import transaction

@transaction.atomic

def create_project(request):
    if request.method == 'POST':
        # Formdan verileri al
        project_name = request.POST.get('proje_adi')
        project_owner = request.POST.get('proje_sahibi')
        project_purpose = request.POST.get('proje_amaci')
        start_date = request.POST.get('baslangic_tarihi')
        end_date = request.POST.get('bitis_tarihi')
        friends = request.POST.getlist('calisacak_kisiler')  # Seçilen arkadaşların listesi
        adam_ay_values = request.POST.getlist('adam_ay_values')  # Kullanıcının girdiği adam/ay oranları

        # Proje oluştur
        project = Proje.objects.create(proje_adi=project_name, proje_sahibi=project_owner, proje_amaci=project_purpose,
                                       baslangic_tarihi=start_date, bitis_tarihi=end_date)

        # Atamaları yap
        for friend, adam_ay in zip(friends, adam_ay_values):
            # Arkadaşın UserProfile'ını al
            friend_profile = UserProfile.objects.get(user__username=friend)

            # Girdiği adam/ay oranını kontrol et
            if float(adam_ay) <= 0 or float(adam_ay) > friend_profile.total_adam_ay:
                # Hata mesajı göster ve atama yapma
                error_message = f"{friend_profile.user.username} için hatalı adam/ay oranı: {adam_ay}"
                return render(request, 'proje_olustur.html', {'error_message': error_message})

            # Atama yap
            assignment = Assignment.objects.create(project=project, assigned_to=friend_profile, adam_ay_orani=adam_ay)

            # Kullanıcının kalan adam/ay oranını güncelle
            friend_profile.total_adam_ay -= float(adam_ay)
            friend_profile.save()

        # Projeyi ve atamaları kaydet
        project.save()

        return redirect('projelerim')  # Başka bir sayfaya yönlendirme

    else:
        # Sayfayı göster
        user_profile = UserProfile.objects.get(user=request.user)
        friends = user_profile.friends.all()
        return render(request, 'proje_olustur.html', {'friends': friends})
