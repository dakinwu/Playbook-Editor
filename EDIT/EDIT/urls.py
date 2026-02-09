from django.urls import re_path
from django.contrib import admin
from django.urls import path, include
import views
import chatbot.views
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from ms_identity_web.django.msal_views_and_urls import MsalViews

msal_urls = MsalViews(settings.MS_IDENTITY_WEB).url_patterns()
urlpatterns = [     
    path('admin/', admin.site.urls),
    # # path("accounts/", include("accounts.urls")), # new
    path("accounts/", include("django.contrib.auth.urls")),
    # path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("", views.home, name="index"),
    # path('test', views.main_ken),

    path('edit/', views.edit, name='edit'),
    path('save_doc/', views.save_doc, name='save_doc'),
    # path('hr_check/', views.hr_check, name='hr_check'),
    # path('chatbot/', views.chatbot, name='chatbot'),
    path('knowledge_chat/', chatbot.views.knowledge_chat, name='knowledge_chat'),
    path(f'{settings.AAD_CONFIG.django.auth_endpoints.prefix}/',include(msal_urls)),
    path('send_email/', views.send_email, name='send_email'),
    path('save_friends/', views.save_friends, name='save_friends'),
    path('save_comment/<str:user>/', views.save_comment, name='save_comment'),
    path('checklist/<str:token>/', views.checklist, name='checklist'),

]