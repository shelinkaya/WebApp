#argemerkezi/takipsistemi/models.py:
from django.db import models
from django.contrib.auth.models import User
import datetime


GENDER_CHOICES = [
    ('male', 'Erkek'),
    ('female', 'Kadın'),
    ('other', 'Diğer'),
]
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    birth_date = models.DateField(default=datetime.date.today)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='other')
    contact_info = models.CharField(max_length=255, default='')
    occupation = models.CharField(max_length=100,default='')
    expertise = models.CharField(max_length=255,default='')
    bio = models.TextField(default="")
    title = models.CharField(max_length=100)  # Örnek olarak eklenmiş bir alan
    friends = models.ManyToManyField("self", blank=True)  # Örnek olarak eklenmiş bir alan
    unit = models.CharField(max_length=100, blank=True)  # Örnek olarak eklenmiş bir alan
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    class Meta:
        verbose_name_plural = "UserProfiles"

    def __str__(self):
        return self.user.username
    notes = models.TextField(blank=True, null=True)

class Project(models.Model):
    name = models.CharField(max_length=200)
    summary = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

class Assignment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    allocation = models.FloatField(default=0.0)

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    day = models.CharField(max_length=10)  # Haftanın günü
    content = models.TextField()  # Not içeriği

    def __str__(self):
        return f"{self.user.username} - {self.day}"

#class FriendshipRequest(models.Model):
    #from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_requests')
    #to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_requests')
    #is_accepted = models.BooleanField(default=False)

    #def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username}"

class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True, null=True)

class FriendshipRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)

# messaging/models.py

class Chat(models.Model):
    participants = models.ManyToManyField(User)
    title = models.CharField(max_length=255)

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class Etkinlik(models.Model):
    title = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

class Proje(models.Model):
    proje_adi = models.CharField(max_length=100)
    proje_sahibi = models.CharField(max_length=100)
    proje_amaci = models.TextField()
    baslangic_tarihi = models.DateField()
    bitis_tarihi = models.DateField()
    # Diğer gerekli alanları buraya ekleyebilirsiniz.
class GanttSema(models.Model):
    proje = models.ForeignKey(Proje, on_delete=models.CASCADE)
    gantt_data = models.JSONField()  # JSON olarak Gantt verilerini saklamak için