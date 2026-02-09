import django
from django.contrib import admin
from .models import Bible, friends, check
 
# Register your models here.

class BibleAdmin(admin.ModelAdmin):
    list_display = ["ui_order","session_tag","html_code","navbar_code"]
admin.site.register(Bible, BibleAdmin)

class friendsAdmin(admin.ModelAdmin):  
    list_display = ["ad_user"]
admin.site.register(friends, friendsAdmin)

class checkAdmin(admin.ModelAdmin):  
    list_display = ["ad_user"]
admin.site.register(check, checkAdmin)