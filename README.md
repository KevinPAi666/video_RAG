# video_RAG
## 痛點
作者參與的讀書會影片數眾多，某一天想到的問題不確定有沒有在影片中出現過，或是出現在什麼時候。藉著相似影片名稱並將整段影片看了一輪，費時費力。

## 功能簡介
下載某資料夾中所有歷史影片，做成中文字幕檔後轉換成embedding提供給後續RAG使用。

內建登入系統，管理員才可以更新影片; 一般使用者只能問問題。

這套系統實現了可以從對話框中輸入想知道的內容，送出後得到該內容在哪支影片的幾分幾秒出現，以及其他可能也是相關內容的推薦。
## 前置作業
1. openai api key
2. google cloud 服務帳戶
    - 至 https://console.cloud.google.com/apis/credentials
    - 建立憑證 > 服務帳戶 > (建立完成) >> 金鑰 > 建立新的金鑰(json)

3. google cloud drive 資料夾共享網址
    - 設置成"知道連結的任何人"
    - 複製連結 "https://drive.google.com/file/d/$GOOGLE_DRIVE_FOLDER_ID/view?usp=sharing" 取中間 "GOOGLE_DRIVE_FOLDER_ID"

4. 填入 .env 
5. 強大的GPU電腦。(轉換字幕需要)

## 運行方式
<pre><code>bash
$ docker build -t video_rag .
$ docker run build -p 8000:8000 video_rag
</code></precode>
