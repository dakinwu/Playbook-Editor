from django.shortcuts import render
 
# Create your views here.
 
import os
import json
import codecs
import requests
import datetime
import shutil
from urllib.parse import quote
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseRedirect
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
 
 
import openai
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import AzureOpenAI
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
 
import time
from langchain.document_transformers import LongContextReorder
 
OPENAI_API_KEY = "1903f5c231e94d599907d1441acc1e49"
OPENAI_DEPLOYMENT_NAME = "Group4GPT"
OPENAI_EMBEDDING_MODEL_NAME = "Group4embedding"
MODEL_NAME = 'gpt-35-turbo'
openai.api_type = "azure"
openai.api_base = "https://makalotopenaig4.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
os.environ["OPENAI_API_VERSION"] = "2023-03-15-preview"
openai.api_version = os.environ["OPENAI_API_VERSION"]
key = "1903f5c231e94d599907d1441acc1e49"
os.environ["OPENAI_API_KEY"] = key
openai.api_key = os.environ["OPENAI_API_KEY"]
 
### HuggingFace Embedding
model_name = "sentence-transformers/all-MiniLM-L6-v2"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)
 
from datetime import datetime

# @csrf_exempt
# def kb_chatbot(request):
#     upload = False
#     show_file_upload = False
 
#     knowledge_base_list = os.listdir('static/knowledge_base/')
 
#     if request.method == 'POST':
#         return JsonResponse({'bot_response': '請選擇知識庫進行問答，謝謝！'})
#     else:
#         return render(request, 'chatbot.html', locals())
 
 
@csrf_exempt
def knowledge_chat(request):
    upload = False
    show_file_upload = True
    knowledge_base_list = os.listdir('static/knowledge_base/')
    data_list = os.listdir(f'static/knowledge_base/bible')
    data_list.remove('temp_embeddings') if 'temp_embeddings' in data_list else None
    data_list.remove('ask_kb_history.txt') if 'ask_kb_history.txt' in data_list else None
 
    if request.method == 'POST':
 
        if 'temp_embeddings' in os.listdir(f'static/knowledge_base/bible'):
            temp_embeddings = FAISS.load_local(f'static/knowledge_base/bible/temp_embeddings', embeddings)
 
            ### Prompt Template Customization
            prompt_template = """參考資訊：{context}\n針對以上的問題:{question}？\n僅用繁體中文回答，並且回答完一個問題就立即停止："""
            # prompt_template = """請依據下列的參考資訊 ({context}) 進行回答問題，如果找不到答案，請直接回答找不到，請勿捏造訊息，問題是 ({question}) ，請勿過多空格或是換行符號、請用繁體中文回答、回答完問題不要再生成無關問題的資料:"""
            prompt_template = """【資訊】{context}\n請參考【資訊】不要參考上面的格式，盡可能精簡地回答問題：{question}"""

            PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
 
            chain = load_qa_chain(AzureOpenAI(openai_api_key=OPENAI_API_KEY, deployment_name=OPENAI_DEPLOYMENT_NAME, model_name=MODEL_NAME, temperature=0), chain_type="stuff", prompt=PROMPT)
            inquiry = request.POST['user_input']
            docs = temp_embeddings.similarity_search(inquiry)
            docs2 = temp_embeddings.similarity_search_with_score(inquiry)
            print(inquiry)
            # with open(f'static/test.txt', 'a', encoding='UTF-8') as f:
            #     f.write(str(docs1))
            #     f.write(str(docs2))
            #     f.close()
            
            response = chain.run(input_documents=docs, question=inquiry)
            show_referrences = []
            search_results = []
            for i in range(len(docs)):
                data = {}
                data['page_content'] = docs[-(i+1)].page_content
                data['source'] = docs[-(i+1)].metadata['source']
                # data['page'] = docs[-(i+1)].metadata['page']
                data['score'] = str(round(docs2[-(i+1)][-1],2))
                show_referrences.append(data)
                search_results.append(docs[-(i+1)].page_content)
                # show_referrences.append('\n')
 
            ########################################################################################################################
            ### References Double Checks ###
            ########################################################################################################################
            time_a = time.time()
            # # Get embeddings.
            # embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            # Create a retriever
            retriever_dc = Chroma.from_texts(search_results, embedding=embeddings).as_retriever(
                search_kwargs={"k": 4}
            )
            # Get relevant documents ordered by relevance score
            docs_dc = retriever_dc.get_relevant_documents(str(response))
            # print(docs_dc[0].page_content)
            time_b = time.time()
            print(time_b - time_a)
 
            show_referrences_dc = []
 
            for j in range(len(docs_dc)):
                for k in show_referrences:
                    if k['page_content'] == docs_dc[j].page_content:
                        show_referrences_dc.append(k)
 
            print(time.time() - time_b)
 
            show_referrences = show_referrences_dc
            
            # GPT
            start = datetime.now()

            # append page_contents' from show_referrences
            # data = show_referrences[0]['page_content']
            
            data = ""
            for i in show_referrences:
                data += i['page_content'] + '\n'
            
            ask = data + "\n，如果找不到答案，請直接回答找不到，請勿捏造訊息。我的問題是：" + inquiry
            
            response = openai.ChatCompletion.create(
                engine="Group4GPT",
                messages = [{"role": "user", "content": ask}],
                temperature=0.7,
                max_tokens=800,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None)
            end = datetime.now()
            
            with open('testing123.txt', 'w') as f:
             f.write(response.choices[0].message['content'])
            
            # print(response.choices[0].message['content'])
            
            print(end-start)
            ########################################################################################################################
            ### References Double Checks - END ###
            ########################################################################################################################
 
            src = show_referrences #+ str(temp_embeddings.docstore._dict)
 
            ### 歷史問答資料
 
            # ask_history = f'static/knowledge_base/bible/' + 'ask_kb_history.txt'
            # with open(ask_history, 'a', encoding='UTF-8') as f:
            #     f.write('---------------------【ASK】---------------------'+'\n')
            #     f.write(str(inquiry))
            #     f.write('-------------------【RESPONSE】------------------'+'\n')
            #     f.write(str(response))
                # for i in range(len(docs)):
                #     history_data = {}
                #     history_data['page_content'] = docs[-(i+1)].page_content
                #     history_data['source'] = docs[-(i+1)].metadata['source']
                #     # history_data['page'] = docs[-(i+1)].metadata['page']
                #     history_data['score'] = str(round(docs2[-(i+1)][-1],2))
                #     f.write(f'-----------------【Referrences {str(i)}】-----------------'+'\n')
                #     f.write(str(history_data) +'\n')
                #     f.write('-----------------------------------------------'+'\n')
 
            return JsonResponse({'bot_response': response.choices[0].message['content']}) # , "source" : src / .replace('<|im_end|>','').split('\n')[0]
 
        else:
            return JsonResponse({'bot_response': '請上傳知識庫文件，再進行問答，謝謝！'})
    else:
        return redirect('/main/')
 
 
# def create_kb(request):
#     if request.method == 'POST':
#         knowledge_base = request.POST['knowledge_base_name']
#         os.mkdir('static/knowledge_base/' + knowledge_base)
#         messages.info(request, "【成功創建知識庫】"+knowledge_base)
#         return redirect('/chatbot/')
#     else:
#         messages.info(request, "【創建知識庫失敗】"+knowledge_base)
#         return redirect('/chatbot/')
 
# def delete_kb(request):
#     if request.method == 'POST':
#         knowledge_base = request.POST['knowledge_base_name']
#         shutil.rmtree('static/knowledge_base/' + knowledge_base)
#         messages.info(request, "【成功刪除知識庫】"+knowledge_base)
#         return redirect('/chatbot/')
#     else:
#         messages.info(request, "【刪除知識庫失敗】"+knowledge_base)
#         return redirect('/chatbot/')
 
# def upload_docs(request):
#     if request.method == 'POST':
#         knowledge_base = request.POST['knowledge_base_name']
#         uploaded_files = request.FILES.getlist('files')
#         fs = FileSystemStorage()
#         upload_message=''
 
#         for file in uploaded_files:
#             save_path = f'static/knowledge_base/{knowledge_base}/{file.name}'
 
#             if os.path.exists(save_path):
#                 upload_message += f'【上傳附件{save_path.split("/")[-1]}失敗，檔案名稱重複，請重新命名】'
#             elif ('.pdf' in save_path) or ('.PDF' in save_path):
#                 filename = fs.save(save_path, file)
#                 upload_message += f'【上傳附件{save_path.split("/")[-1]}成功】'
 
#                 pdf_loader = PyPDFLoader(save_path)
#                 documents = pdf_loader.load()
#                 text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#                 docs = text_splitter.split_documents(documents)
 
#                 if 'temp_embeddings' in os.listdir(f'static/knowledge_base/{knowledge_base}'):
#                     temp_embeddings = FAISS.load_local(f'static/knowledge_base/{knowledge_base}/temp_embeddings', embeddings)
#                     cur_embeddings = FAISS.from_documents(docs, embeddings)
#                     temp_embeddings.merge_from(cur_embeddings)
#                     temp_embeddings.save_local(f'static/knowledge_base/{knowledge_base}/temp_embeddings')
#                 else:
#                     temp_embeddings = FAISS.from_documents(docs, embeddings)
#                     temp_embeddings.save_local(f'static/knowledge_base/{knowledge_base}/temp_embeddings')
#             else:
#                 upload_message += f'【上傳附件{save_path.split("/")[-1]}失敗，檔案格式錯誤，需為PDF檔案】'
#             upload_message += '\\n'
#         messages.info(request, upload_message)
 
#         return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
#     else:
#         return render(request, 'chatbot.html', locals())
 
# def delete_docs(request):
#     if request.method == 'POST':
#         knowledge_base = request.POST['knowledge_base_name']
#         detete_file = request.POST.getlist('file_to_delete')
#         delete_message = ''
 
#         for file in detete_file:
#             name_without_extension = os.path.splitext(file)[0]
#             extension = os.path.splitext(file)[1]
#             delete_path = f'static/knowledge_base/{knowledge_base}/{name_without_extension + extension}'
 
#             if os.path.exists(delete_path):
#                 delete_message += f'【檔案：{name_without_extension + extension}已刪除成功】'
#                 os.remove(delete_path)
#             else:
#                 delete_message += f'【檔案：{name_without_extension + extension} 刪除失敗】'
#             delete_message += '\\n'
 
#         ### delete embeddings
#         shutil.rmtree(f'static/knowledge_base/{knowledge_base}/temp_embeddings')
#         data_list = os.listdir(f'static/knowledge_base/{knowledge_base}')
#         data_list.remove('ask_kb_history.txt') if 'ask_kb_history.txt' in data_list else None
#         if len(data_list) >= 1:
#             text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#             for i in data_list:
#                 file_path = f'static/knowledge_base/{knowledge_base}/{i}'
#                 pdf_loader = PyPDFLoader(file_path)
#                 documents = pdf_loader.load()
#                 docs = text_splitter.split_documents(documents)
 
#                 if 'temp_embeddings' in os.listdir(f'static/knowledge_base/{knowledge_base}'):
#                     temp_embeddings = FAISS.load_local(f'static/knowledge_base/{knowledge_base}/temp_embeddings', embeddings)
#                     cur_embeddings = FAISS.from_documents(docs, embeddings)
#                     temp_embeddings.merge_from(cur_embeddings)
#                     temp_embeddings.save_local(f'static/knowledge_base/{knowledge_base}/temp_embeddings')
#                 else:
#                     temp_embeddings = FAISS.from_documents(docs, embeddings)
#                     temp_embeddings.save_local(f'static/knowledge_base/{knowledge_base}/temp_embeddings')
 
#         messages.info(request, delete_message)
 
#         return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
#     else:
#         return render(request, 'chatbot.html', locals())