import os
import re
import sys
import json
import time
import codecs
import socket
import secrets
import requests
import datetime
import threading
import pandas as pd
import win32com.client
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from bs4 import BeautifulSoup
from django.db.models import Q
from urllib.parse import quote
from os import listdir,getcwd
from os.path import isfile, join
from langchain.vectorstores import FAISS # new
from newbie.models import Bible, friends, check
from django.urls import reverse
from textsplitter.chinese_text_splitter import ChineseTextSplitter # new
from bs4.element import Comment
from django.contrib import messages
from django.core.mail import send_mail
from langchain.document_loaders import TextLoader # new
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from langchain.text_splitter import CharacterTextSplitter # new
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from langchain.embeddings import HuggingFaceEmbeddings # new
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse

# new
model_name = "sentence-transformers/all-MiniLM-L6-v2"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

@csrf_exempt
# --Older Version--
# def get_current_ip():
#     hostname = socket.gethostname()
#     ip_address = socket.gethostbyname(hostname)
#     return ip_address

# def update_url(request, current_user, current_form):
#     current_ip = get_current_ip()

def get_current_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]  # Take the first IP in the list
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    return ip_address
def update_url(request, current_user, current_form):
    current_ip = get_current_ip(request)
    url = "https://" + current_ip + ":7861/checklist/" + request.identity_context_data.username
    current_user.url = url
    token = secrets.token_urlsafe()
    if current_user.token == "":
        current_user.token = token
    if current_form.token == "":
        current_form.token = token
    current_user.save()
    current_form.save()

def home(request):
    # if request.identity_context_data.authenticated:
    today = datetime.date.today()
    filename = today.strftime('%Y-%m-%d') + '.json'
    filepath = r"static/knowledge_base/"+filename
    sessions = Bible.objects.all()
    bible = Bible.objects.get(ui_order = 0)
    navbar = bible.navbar_code
    current_user = friends.objects.get_or_create(ad_user=request.identity_context_data.username)
    current_user = check.objects.get_or_create(ad_user=request.identity_context_data.username)
    current_user = friends.objects.get(ad_user=request.identity_context_data.username)
    current_form = check.objects.get(ad_user=request.identity_context_data.username)
    update_url(request, current_user, current_form)
    return render(request, 'home.html', locals())
                      
def send_email(request):
    if request.method == 'POST':
        bossname = request.POST.get('bossname')
        current_user = friends.objects.get(ad_user=request.identity_context_data.username) 
        sender = 'url-notify@makalot.com.tw'
        receivers = [bossname+'@makalot.com.tw']
        
        current_ip = get_current_ip()
        url = "https://" + current_ip + ":7861/checklist/" + current_user.token
        
        message = MIMEText(url, 'html', 'utf-8')
        message['From'] = Header("Sign-Up Url from "+request.identity_context_data.username, 'utf-8')   # 发送者
        message['To'] =  ", ".join(receivers)
        
        subject = "請協助簽名！"
        message['Subject'] = Header(subject, 'utf-8')
        
        try:
            smtpObj = smtplib.SMTP('nt-tp-email.makalot.com')
            smtpObj.sendmail(sender, receivers, message.as_string())
            smtpObj.quit()
            print("success")
            return JsonResponse({"status": "success"})
        except smtplib.SMTPException as e:
            print ("Error")
            return JsonResponse({"status": "error", "message": str(e)})
        # return redirect('/')
    return JsonResponse({"status": "error", "message": "Invalid request"})
    # else:
    #     return redirect('/')

def save_friends(request):
    if request.method == 'POST':
        current_user = friends.objects.get(ad_user=request.identity_context_data.username)
        current_user.field1 = request.POST.get('field1', '')
        current_user.field2 = request.POST.get('field2', '')
        current_user.field3 = request.POST.get('field3', '')
        current_user.field4 = request.POST.get('field4', '')
        current_user.field5 = request.POST.get('field5', '')
        current_user.field6 = request.POST.get('field6', '')
        current_user.field7 = request.POST.get('field7', '')
        current_user.field8 = request.POST.get('field8', '')
        current_user.field9 = request.POST.get('field9', '')
        current_user.field10 = request.POST.get('field10', '')
        current_user.field11 = request.POST.get('field11', '')
        current_user.field12 = request.POST.get('field12', '')
        current_user.field13 = request.POST.get('field13', '')
        current_user.field14 = request.POST.get('field14', '')
        current_user.field15 = request.POST.get('field15', '')
        current_user.field16 = request.POST.get('field16', '')
        current_user.field17 = request.POST.get('field17', '')
        current_user.field18 = request.POST.get('field18', '')
        current_user.save()
        return redirect('/')
    else:
        return redirect('/')
    
@csrf_exempt
def save_comment(request, user):
    show_alert = False
    original_user = check.objects.get(ad_user=user)
    if user == request.identity_context_data.username:
        show_alert = True
        return render(request, 'table.html', locals())
    if request.identity_context_data.authenticated:
        token = original_user.token
        if request.method == 'POST':
            original_user.field22 = request.POST['field22']
            original_user.save()
            return redirect('/checklist/'+token)
        return render(request, 'table.html', locals())
    else:
        return redirect('/checklist/'+token)

def get_user_from_token(token):
    user = get_object_or_404(friends, token=token)
    return user

@csrf_exempt
def checklist(request, token):
    show_alert = False
    user = get_user_from_token(token)
    original_user = check.objects.get(ad_user=user.ad_user)
    if not user:
        return HttpResponse("無效的Token", status=403)
    if request.identity_context_data.authenticated:
        if request.identity_context_data.username == user.ad_user:
            show_alert = True
            return render(request, 'table.html', locals())
        current_user = request.identity_context_data.username
        if request.method == 'POST':
            field_name = request.POST.get('field_name')
            if hasattr(original_user, field_name):
                now = datetime.datetime.now()
                date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                setattr(original_user, field_name, date_time + "\n" + current_user)
                original_user.save()
                return redirect('/checklist/'+token)
        return render(request, 'table.html', locals())
    else:
        return render(request, 'table.html', locals())

def custom_permission_denied_view(request, exception):
    return render(request, '403.html', status=403)

def hr_check(func):
    def wrapper(request, *args, **kwargs):
        if request.identity_context_data.authenticated:
            if request.identity_context_data.username == 'Dakin Wu (Taipei, 吳岱錡)':
                return func(request, *args, **kwargs)
            else:
                custom_permission_denied_view()
        else:
            custom_permission_denied_view()
    return wrapper

@hr_check
def edit(request):
    sessions = Bible.objects.all()
    bible = Bible.objects.get(ui_order = 0)
    navbar = bible.navbar_code
    return render(request, 'edit.html', {'sessions': sessions, 'navbar': navbar})

@hr_check
def save_doc(request):
    if request.method == 'POST':
        content = request.POST['show_doc']

        if request.user.groups.filter(name='Newbie').exists():
            bible = Bible.objects.get(ui_order=0)
            bible.form_code = content
            bible.save()
            if request.POST.get('continue_editing') == 'true':
                time.sleep(1)
                return redirect('/edit/')
            else:
                return redirect('/')

        # 1. 解析 HTML
        soup = BeautifulSoup(content, 'html.parser')
        headers = soup.find_all(['h1', 'h2']) 
        
        # 2. 生成導航欄
        navbar_items = ''
        for index, header in enumerate(headers):
            header_id = f"header-{index}"  # 生成唯一的id
            header['id'] = header_id  # 將id設定到header
            text = header.get_text().replace("#", "")
            cleaned_text = re.sub(r'http://[^\s]+', '', text)
            css_classes = ["nav-item", "section-title"]
            if header.name == 'h2':
                css_classes.append("sub-section-title")
            combined_class = " ".join(css_classes)
            navbar_items += f'<li class="{combined_class}"><a class="nav-link scrollto" href="#{header_id}">{cleaned_text}</a></li>'

        navbar = '''
        <nav id="docs-nav" class="docs-nav navbar navbar-expand-md">
            <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNavDropdown" aria-controls="navbarNavDropdown" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNavDropdown">
                <ul class="section-items list-unstyled nav flex-column pb-3">
                ''' + navbar_items + '''
                </ul>
            </div>
        </nav>
        '''
        existing_content = ""
        with codecs.open(r"C:/Users/dakinwu/Downloads/EDIT/Output.txt", "r", encoding="utf-8") as text_file:
            existing_content = text_file.read()

        texts = soup.findAll(string=True)
        visible_texts = [(t, t.parent) for t in filter(tag_visible, texts)]
        results = []
        for i, (text, parent) in enumerate(visible_texts):
            text = text.strip().replace("#", "")
            if not text:
                continue
            if i > 0:
                prev_parent = visible_texts[i-1][1]
                if prev_parent.name in ["b", "u"] or parent.name in ["b", "u"]:
                    results.append(text)
                    continue
            results.append("\n" + text)
        final = "".join(results)

        if final != existing_content:
            with codecs.open(r"C:/Users/dakinwu/Downloads/EDIT/Output.txt", "w", encoding="utf-8") as text_file:
                text_file.write(final)

            bible = Bible.objects.get(ui_order=0)
            bible.html_code = content
            bible.navbar_code = navbar
            bible.save()

            # def output():
            #     url = "http://192.168.4.39:7860/local_doc_qa/update_file?knowledge_base_id=OMG&old_doc=Output.txt"
            #     files = {'new_doc': open('C:/Users/dakinwu/Downloads/EDIT/Output.txt', 'rb')}
            #     data = {"knowledge_base_id": "OMG"}
            #     uploaded = requests.post(url, files=files, data=data)
            # new
            def output():
                # raw_documents = TextLoader(r"C:/Users/dakinwu/Downloads/EDIT/Output.txt", autodetect_encoding=True).load()
                # text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                # documents = text_splitter.split_documents(raw_documents)

                loader = TextLoader(r"C:/Users/dakinwu/Downloads/EDIT/Output.txt", autodetect_encoding=True)
                textsplitter = ChineseTextSplitter(pdf=False, sentence_size=200)
                docs = loader.load_and_split(textsplitter)
                temp_embeddings = FAISS.from_documents(docs, embeddings)
                temp_embeddings.save_local(f'static/knowledge_base/bible/temp_embeddings')

            event = threading.Event()   # 註冊事件
            b = threading.Thread(target=output)
            b.start()

        bible = Bible.objects.get(ui_order=0)
        bible.html_code = content
        bible.navbar_code = navbar
        bible.save()
        if request.POST.get('continue_editing') == 'true':
            time.sleep(1)
            return redirect('/edit/')
        else:
            return redirect('/')

# def chatbot(request):
#     today = datetime.date.today()
#     filename = today.strftime('%Y-%m-%d') + '.json'
#     filepath = r"static/knowledge_base/"+filename
#     if request.method == 'POST':
#         user_input = request.POST['user_input']
#         url = "http://192.168.4.39:7860/chat"
#         default_history = [
#             ["你是聚陽數轉部，LLM 團隊所開發的智能知識庫平台。", "了解，我是是聚陽數轉部，LLM 團隊所開發的智能知識庫平台。"],
#             ["聚陽數轉部 LLM 團隊成員包含：陳肯、Dakin。", "了解，聚陽數轉部 LLM 團隊成員包含：陳肯、Dakin。"]
#         ]

#         if os.path.isfile(filepath):
#             try:
#                 with open(filepath, 'r', encoding='utf-8') as file:
#                     history = [json.loads(line) for line in file]
#             except Exception as e:
#                 print(f"讀取文件錯誤：{e}")
#                 history = default_history
#         else:
#             history = default_history
#         myobj ={
#           "question": user_input,
#           "history": history
#         }
#         bot_response = requests.post(url, json = myobj)
#         history = json.loads(bot_response.text)["history"]
#         with codecs.open(filepath, "w", encoding = "utf-8") as f:
#             for dict in history:
#                 f.write(json.dumps(dict, ensure_ascii = False) + "\n")
#         bot_response = json.loads(bot_response.text)["response"]
#         return JsonResponse({'bot_response': bot_response})
#     else:
#         return redirect('/main/')

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

# def knowledge_chat(request):
#     if request.method == 'POST':
#         user_input = request.POST['user_input']
#         know = "http://192.168.4.39:7860/local_doc_qa/local_doc_chat"
#         myobj ={
#           "knowledge_base_id": "OMG",
#           "question": user_input,
#           "history": []
#         }
#         bot_res = requests.post(know, json = myobj)
#         bot_response = json.loads(bot_res.text)["response"]
#         src = json.loads(bot_res.text)["source_documents"]
#         src = [i[:-2] for i in src]
#         src = "\n\n".join(src)
#         if src == "":
#             return JsonResponse({'bot_response': bot_response})
#         else:
#             return JsonResponse({'bot_response': bot_response, "source" : "\n資料來源："+src})
#     else:
# return redirect('/main/')