from django.contrib.auth.models import User  
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile 
from .models import Note,Event, Message, Etkinlik
from .models import Proje
from .models import Chat, Assignment
from django.contrib.auth import authenticate
  
class CustomUserCreationForm(UserCreationForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=[('male', 'Erkek'), ('female', 'Kadın')])
    contact_info = forms.CharField(widget=forms.Textarea)
    profile_picture = forms.ImageField(required=False)
    occupation = forms.CharField()
    expertise = forms.CharField()
    bio = forms.CharField(widget=forms.Textarea)
    accept_terms = forms.BooleanField()

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=[('male', 'Erkek'), ('female', 'Kadın')])
    contact_info = forms.CharField(widget=forms.Textarea)
    profile_picture = forms.ImageField(required=False)
    occupation = forms.CharField()
    expertise = forms.CharField()
    bio = forms.CharField(widget=forms.Textarea)
    accept_terms = forms.BooleanField()

    class Meta:
        model = UserProfile
        fields = ('user', 'name', 'birth_date', 'gender', 'contact_info', 'profile_picture', 'occupation', 'expertise', 'bio', 'accept_terms')

class LoginForm(forms.Form):
    email = forms.EmailField(label='E-posta')
    password = forms.CharField(label='Şifre', widget=forms.PasswordInput)

class ArkadasEkleForm(forms.Form):
    username_or_email = forms.CharField(label="Kullanıcı Adı veya E-posta", max_length=100)

class NotForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['day', 'content']

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'start_date', 'end_date', 'description']

class MessageForm(forms.ModelForm):
    recipient = forms.CharField(max_length=150)
    
    class Meta:
        model = Message
        fields = ['recipient', 'content', 'media_file']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(MessageForm, self).__init__(*args, **kwargs)

    def clean_recipient(self):
        recipient_username = self.cleaned_data.get('recipient')
        try:
            recipient_user = User.objects.get(username=recipient_username)
        except User.DoesNotExist:
            raise forms.ValidationError("Bu kullanıcı bulunamadı.")
        return recipient_user

    def clean(self):
        cleaned_data = super().clean()
        recipient_user = cleaned_data.get('recipient')
        if recipient_user and recipient_user == self.request.user:
            raise forms.ValidationError("Kendi kendinize mesaj gönderemezsiniz.")
        
    def save_message(self, sender):
        recipient_username = self.cleaned_data['recipient']
        content = self.cleaned_data['content']
        media_file = self.cleaned_data['media_file']
        try:
            recipient = User.objects.get(username=recipient_username)
            if recipient != sender:
                chat, created = Chat.objects.get_or_create(participants__in=[sender, recipient])
                message = Message.objects.create(chat=chat, sender=sender, recipient=recipient, content=content, media_file=media_file)
                return message
        except User.DoesNotExist:
            pass
        return None

class EtkinlikForm(forms.ModelForm):
    class Meta:
        model = Etkinlik
        fields = ['title', 'start_date', 'end_date', 'description']

# forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Proje

class ProjeForm(forms.ModelForm):
    projede_calisacak_kisiler = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Proje
        fields = ['proje_adi', 'proje_sahibi', 'proje_amaci', 'baslangic_tarihi', 'bitis_tarihi', 'projede_calisacak_kisiler']



class AssignmentForm(forms.ModelForm):
    # Diğer alanlar burada bulunur

    # Seçilen her bir kişi için ayrı ayrı adam/ay oranı alanları
    adam_ay_oranlari = forms.DecimalField(
        label="Adam/Ay Oranı",
        help_text="Seçili kişiler için ayrı ayrı adam/ay oranı belirtin.",
        widget=forms.NumberInput(attrs={'step': '0.01'}),  # İstenen hassasiyete göre ayarlayabilirsiniz
    )

    class Meta:
        model = Assignment
        fields = ['assigned_to', 'adam_ay_oranlari']

from django import forms
from django.contrib.auth.models import User

class ProjeCalisacakKisiForm(forms.Form):
    username = forms.CharField(label="Kullanıcı Adı")
    adam_ay_orani = forms.DecimalField(label="Çalışacağı Adam/Ay Oranı", widget=forms.NumberInput(attrs={'step': '0.01'}))
