from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from .models import USER_Model
from . import func_chatbot, func_video_process

import os, json


def main(request):
    sys_info, error_msg, question, question_answer = "", "", "", ""
    if str(request.user) == "AnonymousUser":
        account = request.POST.get("account")
        password = request.POST.get("password")
        if request.POST.get("registry"):
            # if account.startswith("ai.free."):
                try:
                    USER_Model.objects.create_user(
                        username=account,
                        password=password
                    )
                    sys_info = "Registry done, please login again."
                except Exception as e:
                    error_msg = str(e)
                    if "UNIQUE constraint failed: VRAG_user_model.username" in error_msg: error_msg = "This account had been registry."

            # else:
                # error_msg = "Wrong account rule, please contact administrator."

        if request.POST.get("login"):
            try:
                USER_Model.objects.get(username=account)
                user_auth = authenticate(request, username=account, password=password)
                login(request, user_auth)
                
            except Exception as e:
                error_msg = str(e)
                if "'AnonymousUser' object has no attribute '_meta'" in error_msg: error_msg = "Wrong account or password."
                if "USER_Model matching query does not exist." in error_msg: error_msg = "Wrong account or password."

    else:
        if request.POST.get('logout'):
            logout(request)

        if request.POST.get('question_ask'):
            question = request.POST.get("user_question")
            if len(question) == 0:
                error_msg = "請輸入問題 !"
            else:
                question_answer = func_chatbot.chat(question)

    return render(request, 'main.html', {"sys_info": sys_info,
                                         "error_msg": error_msg,
                                         "question": question,
                                         "question_answer": question_answer})

def update(request):
    # admin = os.getenv("administrator")
    # admin_list = json.loads(admin)
    # if str(request.user) not in admin_list:
        # return redirect('/')
    video_list = "./file/video_list"
    msg = " "
    
    def load_video():
        with open(video_list, 'r', encoding="utf-8") as r:
            v = json.load(r)
            return v

    if request.POST.get('video_get'):
        func_video_process.videos_get()

    if os.path.isfile(video_list):
        if request.POST.get('videos_download'):
            videos = load_video()
            func_video_process.videos_download(videos)

        if request.POST.get('videos_asr'):
            videos = load_video()
            func_video_process.video_asr(videos)

        if request.POST.get('brain_reload'):
            videos = load_video()
            func_chatbot.brain_reload(videos)
            
    else:
        msg = "Not found any video list file, do step 1 first."

    return render(request, 'update.html', {'msg': msg})

