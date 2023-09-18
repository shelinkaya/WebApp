from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'birth_date', 'gender', 'contact_info', 'occupation', 'expertise', 'bio')

admin.site.register(UserProfile, UserProfileAdmin)




