from google.oauth2 import service_account
from googleapiclient.discovery import build

import subprocess, gdown, os, json

def videos_get():
    """ 格式範本
    videos = {
          "video_name": "video_url",
          "Kafka": "https://drive.google.com/file/d/1HSH6VCVwcPg1nnmeG0HooOf1Wuz2nLXj/view?usp=sharing",
          }
    """
    FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    SERVICE_ACCOUNT_FILE = "./config/gcloud_key.json"

    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)

    query = f"'{FOLDER_ID}' in parents and trashed = false"
    results = service.files().list(
        q=query,
        fields="nextPageToken, files(id, name, webViewLink)",
        pageSize=1000  # 每頁最多可列出 1000 個檔案
    ).execute()

    files = results.get('files', [])

    video_list = {}
    for file in files:
        if '.mp4' in file['name']:
            file_name = file['name'].split('.mp4')[0]
            file_url = file['webViewLink'].replace("view?usp=drivesdk", "view?usp=sharing")
            video_list[file_name] = file_url
            
    videos = json.dumps(video_list, ensure_ascii=False)
    if not os.path.exists("./file/"): os.mkdir("./file/")
    with open("./file/video_list", 'w', encoding="utf-8") as w:
        print(videos, file=w)


def videos_download(videos):
    video_download_location = "./file/videos/"
    if not os.path.exists(video_download_location): os.mkdir(video_download_location)
    
    for video_name, video_url in videos.items():
        video_id = video_url.split("https://drive.google.com/file/d/")[1].split("/view?usp=sharing")[0]
        download_url = f"https://drive.google.com/uc?id={video_id}&export=download"
        gdown.download(download_url, f"{video_download_location}{video_name}.mp4", quiet=False)
        subprocess.run(['ffmpeg', '-i', f"{video_download_location}{video_name}.mp4", '-q:a', '0', '-map', 'a', f"{video_name}.mp3"])


def video_asr(videos):
    video_download_location = "./file/videos/"
    video_asr_location = "./file/videos_srt/"
    if not os.path.exists(video_download_location): os.mkdir(video_download_location)

    for video_name in videos:
        subprocess.run(["whisper", f"{video_download_location}{video_name}.mp3", "--language", "zh", "--model", "medium", "--output_format", "srt", "--output", f"{video_asr_location}{video_name}.srt"])
