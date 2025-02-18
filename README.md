# 備註 :

主程式是PH_Linebot.py。

預處理完的資料是penghu_orignal2.csv

機器學習檔案為ML.py,XGBOOST_predicted.py,XGBOOST_train.py，

分成三個的原因是因為原本是要做及時訓練(ML.py)，
可是展示時要等一分鐘很尷尬改成用模型來預測(XGBOOST_predicted.py,XGBOOST_train.py)。

請事先自行安裝好 ngrok 與 xampp。
xampp 預安裝位置為 C槽，將此資料夾裡的 PHP 檔案放置於 C:/xampp/htdocs 裡，開啟 xampp 後，即可在網站輸入 http://localhost/XXX.php 開啟所需的 PHP 檔。

本研究有建構自己的本地資料庫 (MySQL) ，因此 PHP 檔所產生的地圖資訊，是去讀本地資料庫的數據。

會利用 ngrok 跳轉 PHP localhost 端的問題，而 ngrok 要同時開啟 port 8000 (給 Line Bot) 和 port 80 (給 PHP 動態網頁)，因此要設成多開 port， 到 /Users/XXX/.ngrok2/ngrok.yml裡新增程式碼。
```
tunnels:
  line-bot:
    addr: 8000
    proto: http
    host_header: localhost
    bind_tls: true
  xampp:
    addr: 80
    proto: http
    host_header: localhost:80
    bind_tls: true
   ``` 
ngrok 的指令要下 ngrok start --all，就能透過 [ngrok網址]/XXX.php 進到 PHP 網頁並同時使用 Line Bot。

imgur 禁止了 127.0.0.1 的訪問，所以要測試要用輸入 localhost 不能用 127.0.0.1。

請先安裝 requirement.txt 的套件 pip install -r requirements.txt
