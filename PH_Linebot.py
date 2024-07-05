from flask import Flask, request
#from gevent.pywsgi import WSGIServer
from random import randrange
# 載入 json 標準函式庫，處理回傳的資料格式
import json
# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.models.events import PostbackEvent
#from linebot.exceptions import InvalidSignatureError
#from linebot.models import MessageEvent, TextMessage, TextSendMessage 
from linebot.models import *
#from xgboost import XGBClassifier
import pandas as pd
import numpy as np
import csv
from sklearn.model_selection import train_test_split
#from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import XGBOOST_predicted
import ML
import Search
import Now_weather
import Filter
import Plan2MYSQL
import FlexMessage
import Googlemap_function
import get_location
import plan_location
import PH_Attractions
import urllib.parse


app = Flask(__name__)

access_token = 'h/47RBzNDXh5jWXncB7rZ1GPYKG15fDyuCewrJEJ8Q314NL732t6hQo+Oql/hM/Jn02uU2jCv36wlnPP6XP4p5HG9nUiYfAndRecgTlf2LlQ19m9bc7/Fc3MuguAw0IRCzUiHJjco7gdD1DSD1G2TwdB04t89/1O/w1cDnyilFU='
secret = '1bf0051081f4240f32595d32d374b04c'
line_bot_api = LineBotApi(access_token)              # 確認 token 是否正確
handler = WebhookHandler(secret)                     # 確認 secret 是否正確
PHP_ngrok ="https://9ad4-140-115-158-86.ngrok-free.app"# 80
global age_1 ,gender_1

@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)                    # 取得收到的訊息內容
    global approveGender
    global approveAgeRespond

    try:
        json_data = json.loads(body)                         # json 格式化訊息內容
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
        tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
        type = json_data['events'][0]['message']['type']     # 取得 LINe 收到的訊息類型
        if type=='text':
            msg = json_data['events'][0]['message']['text']  # 取得 LINE 收到的文字訊息
            #功能1
            if msg == "行程規劃"or msg =="6":
                print(msg)
                # line_bot_api.reply_message(tk,TextSendMessage(msg)) # 回傳訊息
                # line_bot_api.reply_message(tk,TextSendMessage("請選擇您的行程規劃天數，將以大數據推薦行程"))
                line_bot_api.reply_message(tk,[TextSendMessage("請選擇您的行程規劃天數，將以大數據推薦行程"),FlexMessage.travel_reply("行程規劃","兩天一夜","兩天一夜","兩天一夜","三天兩夜","三天兩夜","三天兩夜","四天三夜","四天三夜","四天三夜","五天四夜","五天四夜","五天四夜")])               
            #功能2
            elif msg == "景點推薦" or msg == "2":
                print(msg)
                line_bot_api.reply_message(tk, [
                    TemplateSendMessage(
                        alt_text='請選擇是或否',
                        template=ConfirmTemplate(
                            text='您是否要進行永續觀光？',
                            actions=[
                                MessageAction(label='是', text='永續觀光'),
                                MessageAction(label='否', text='一般景點推薦')
                            ]
                        )
                    )
                ])
            elif msg == "一般景點推薦"or msg =="2-2":
                print(msg)
                weather = Now_weather.weather()
                temperature = Now_weather.temperature()
                #weather = "雨"
                # temperature = randrange(15,24)
                arr = np.array([weather])
                tidal = Now_weather.tidal()
                # tidal = randrange(0,2)
                # gender = randrange(0,2)
                age = randrange(15,55)
                global age_1,gender_1 #測試用
                print(arr,gender_1,age_1,tidal,temperature)
                recommend = XGBOOST_predicted.XGboost_recommend2(arr,gender_1,age_1,tidal,temperature)
                encoded_destination = urllib.parse.quote(recommend)
                route_finder_url = f"https://3614-59-102-234-91.ngrok-free.app/test.php?destination={encoded_destination}"
                print(recommend) #推薦的地點是從XGBOOST_predicted來的
                recommend_website,recommend_imgur,recommend_map = PH_Attractions.Attractions_recommend(recommend)#圖片,網址,map是從PH_Attractions來的
                print(recommend_website,recommend_imgur,recommend_map)
                line_bot_api.reply_message(tk,[TextSendMessage("感謝等待\n系統以AI大數據機器學習的方式推薦以下適合您的地點"),
                                                      TextSendMessage(str(recommend)),
                                                      ImageSendMessage(original_content_url=str(recommend_imgur)+".jpg",preview_image_url=str(recommend_imgur)+".jpg"),
                                                      TextSendMessage(recommend_website),
                                                      TextSendMessage(recommend_map)
                                                      ])
                
                # ************************************************************************************************
                
                # line_bot_api.reply_message(
                #     tk,
                #     [
                #         TextSendMessage("感謝等待\n系統已推薦以下適合您的地點"),
                #         TextSendMessage(str(recommend)),
                #         TextSendMessage(f"點擊以下連結查看到該地點的路線：\n{route_finder_url}")
                #     ]
                # )
                
            elif msg == "永續觀光"or msg =="2-1":#測試功能
                print(msg)
                weather = Now_weather.weather()
                temperature = Now_weather.temperature()
                arr = np.array([weather])
                tidal = Now_weather.tidal()
                age = randrange(15,55)
                print(arr,gender_1,age_1,tidal,temperature)
                recommend = XGBOOST_predicted.XGboost_recommend3(arr,gender_1,age_1,tidal,temperature)
                print(recommend) #推薦的地點是從XGBOOST_predicted來的
                recommend_website,recommend_imgur,recommend_map = PH_Attractions.Attractions_recommend1(recommend)#圖片,網址,map是從PH_Attractions來的
                line_bot_api.reply_message(tk,[TextSendMessage("感謝等待\n系統以AI大數據機器學習的方式推薦以下適合您的地點"),
                                                      TextSendMessage(str(recommend)),
                                                      ImageSendMessage(original_content_url=str(recommend_imgur)+".jpg",preview_image_url=str(recommend_imgur)+".jpg"),
                                                      TextSendMessage(recommend_website),
                                                      TextSendMessage(recommend_map)
                                                      ])
                '''
                recommend_website,recommend_imgur,recommend_map = Search.Attractions_recommend(recommend)
                line_bot_api.reply_message(tk,[TextSendMessage("感謝等待\n系統以AI大數據機器學習的方式推薦以下適合您的地點"),
                                                TextSendMessage(str(recommend)),
                                                ImageSendMessage(original_content_url=str(recommend_imgur),preview_image_url=str(recommend_imgur)),
                                                TextSendMessage(recommend_website),
                                                TextSendMessage(recommend_map)
                                                 ])
                '''                                 
            #功能3
            elif msg == "景點人潮"or msg=="3":
                print(msg)
                line_bot_api.reply_message(tk, [TextSendMessage("請點選以下網址，將由大數據為您分析這時間的人潮"),TextSendMessage(str(PHP_ngrok)+"/PengHu_crowd2.php")])
            #功能4
            elif msg == "附近搜尋"or msg =="4":
                print(msg)
                line_bot_api.reply_message(tk,FlexMessage.ask_keyword())
            elif msg == "餐廳" or msg == "停車場" or msg == "住宿":
                print(msg)
                lat,lon=get_location.get_location('C:/Users/wkao_/Desktop/NCLab/penghu project/penghu_csv_file/location.csv')
                Googlemap_function.googlemap_search_nearby(lat,lon,msg)
                carousel_contents=FlexMessage.Carousel_contents('C:/Users/wkao_/Desktop/NCLab/penghu project/penghu_csv_file/recommend.csv')
                line_bot_api.reply_message(tk,FlexMessage.Carousel(carousel_contents)) 
            elif msg == "景點":
                print(msg)                                       # 印出內容
                line_bot_api.reply_message(tk, [TextSendMessage("請點選以下網址，將為您推薦附近景點"),TextSendMessage(str(PHP_ngrok)+"/attration.php")])

            #功能5
            elif msg == "租車" or msg =="5":
                line_bot_api.reply_message(tk, [TextSendMessage("請點選以下網址，將為您推薦租車店家"),TextSendMessage(str(PHP_ngrok)+"/car_rent.php")])

            # # 測試用
            # elif msg == "資料":
            #     print(msg)
            #     global age_1
            #     print(age_1)
            #     reply = f"您目前的年齡是: {age_1} 歲"
            #     line_bot_api.reply_message(tk, TextSendMessage(reply))

        
                
            #功能6
            elif msg == "搜集資料&修改資料"or msg=="1":
                print(msg)
                line_bot_api.reply_message(tk,TextSendMessage("請輸入你的年紀"))
                approveAgeRespond=True
            elif approveAgeRespond==True:
                try:
                    age=msg #儲存age
                    print("detect age=",age)
                    if 0<=int(age) and int(age)<=120:
                        age_1=int(age) #測試用
                        approveAgeRespond=False
                        message=FlexMessage.gender_reply("性別類型","請輸入您的性別","男","男","男","女","女","女","其他","其他","其他")
                        line_bot_api.reply_message(tk,message)
                        approveGender=True

            
                    #年紀不合常理
                    else:
                        print("data overflow or underflow", age)
                        line_bot_api.reply_message(tk,TextSendMessage("請輸入\"正確年紀\""))
                #其他錯誤
                except Exception as e:
                    print("age type error", age)
                    line_bot_api.reply_message(tk,TextSendMessage("請輸入\"正確年紀\""))
                 
            else :
                print(msg)                                       # 印出內容
                reply = msg
                # line_bot_api.reply_message(tk,TextSendMessage(reply))# 回傳訊息

        if type=='location':
                add = json_data['events'][0]['message']['address']  # 取得 LINE 收到的文字訊息
                lat = json_data['events'][0]['message']['latitude']  # 取得 LINE 收到的文字訊息
                lon = json_data['events'][0]['message']['longitude']  # 取得 LINE 收到的文字訊息
                print(add, lat, lon)
                with open('C:/Users/wkao_/Desktop/NCLab/penghu project/penghu_csv_file/location.csv', 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([add, lat, lon])
                line_bot_api.reply_message(tk,TextSendMessage("資料儲存完畢\n請根據您的需求輸入2~6,來獲得相對應的功能:\n2.景點推薦\n3.景點人潮\n4.附近搜尋\n5.租車\n6.行程規劃"))
                print("結束使用\"收集資料功能\" \n------------------") 

    except:
        print(body)                                          # 如果發生錯誤，印出收到的內容
    return 'OK'                                              # 驗證 Webhook 使用，不能省略

@handler.add(PostbackEvent)
def handle_postback(event):
    # 取得 Postback Action 傳送的資料
    postback_data = event.postback.data
    if postback_data =="兩天一夜":
            global age_1,gender_1 #測試用
            print("2days")
            print(gender_1)
            gender = randrange(0,2)
            age = randrange(15,55)
            file='C:/Users/wkao_/Desktop/NCLab/penghu project/penghu_csv_file/plan_2day.csv'
            plan_data = pd.read_csv(file,encoding='utf-8-sig')
            userID = ML.XGboost_plan(plan_data,gender_1,age_1)  
            print(userID,gender,age)
            Filter.filter(file,userID)
            Plan2MYSQL.plan2mysql('C:/Users/wkao_/Desktop/NCLab/penghu project/penghu_csv_file/plan.csv')

            # _____________________測試________________________________________________
            # 從 location.csv 檔案中獲取最新的位置資訊
            lat, lon = get_location.get_location('C:/Users/wkao_/Desktop/NCLab/penghu project/penghu_csv_file/location.csv')
            print("lat and lon :", lat ,lon)
            # 將位置資訊加入 URL
            url = f"{PHP_ngrok}/test_v3.php?lat={lat}&lng={lon}"
            line_bot_api.reply_message(event.reply_token, [
            TextSendMessage("以使用機器學習依據相關性，找尋過往數據最適合您的兩天一夜行程"),
            TextSendMessage(url)
            ])
            # _____________________測試________________________________________________

            # line_bot_api.reply_message(event.reply_token, [TextSendMessage("以使用機器學習依據相關性，找尋過往數據最適合您的兩天一夜行程"),TextSendMessage(str(PHP_ngrok)+"/PengHu_plan.php")])
            
    elif postback_data =="三天兩夜":
            print("3days")
            gender = randrange(0,2)
            age = randrange(15,55)
            file='C:/Users/wkao_/Desktop/NCLab/penghu project/penghu_csv_file/plan_3day.csv'
            plan_data = pd.read_csv(file,encoding='utf-8-sig')
            userID = ML.XGboost_plan(plan_data,gender,age)  
            print(userID)
            Filter.filter(file,userID)
            Plan2MYSQL.plan2mysql('C:/Users/wkao_/Desktop/NCLab/penghu project/penghu_csv_file/plan.csv')
            line_bot_api.reply_message(event.reply_token, [TextSendMessage("以使用機器學習依據相關性，找尋過往數據最適合您的三天兩夜行程"),TextSendMessage(str(PHP_ngrok)+"/PengHu_plan.php")])
    elif postback_data =="四天三夜":
            print("4days")
            gender = randrange(0,2)
            age = randrange(15,55)
            file='C:/Users/wkao_/Desktop/NCLab/penghu project/penghu_csv_file/plan_4day.csv'
            plan_data = pd.read_csv(file,encoding='utf-8-sig')
            userID = ML.XGboost_plan(plan_data,gender,age)  
            print(userID)
            Filter.filter(file,userID)
            Plan2MYSQL.plan2mysql('C:/Users/wkao_/Desktop/NCLab/penghu project/penghu_csv_file/plan.csv')
            line_bot_api.reply_message(event.reply_token, [TextSendMessage("以使用機器學習依據相關性，找尋過往數據最適合您的四天三夜行程"),TextSendMessage(str(PHP_ngrok)+"/PengHu_plan.php")])
    elif postback_data =="五天四夜":
            print("5days")
            gender = randrange(0,2)
            age = randrange(15,55)
            file='C:/Users/wkao_/Desktop/NCLab/penghu project/penghu_csv_file/plan_5day.csv'
            plan_data = pd.read_csv(file,encoding='utf-8-sig')
            userID = ML.XGboost_plan(plan_data,gender,age)  
            print(userID)
            Filter.filter(file,userID)
            Plan2MYSQL.plan2mysql('C:/Users/wkao_/Desktop/NCLab/penghu project/penghu_csv_file/plan.csv')
            line_bot_api.reply_message(event.reply_token, [TextSendMessage("以使用機器學習依據相關性，找尋過往數據最適合您的五天四夜行程"),TextSendMessage(str(PHP_ngrok)+"/PengHu_plan.php")])
    elif postback_data=="男" or postback_data=="女" or postback_data=="其他":

            # gender=postback_data
            # gender=FlexMessage.classify_gender(gender)
            # global gender_1 #測試用
            gender_1=postback_data
            gender_1=FlexMessage.classify_gender(gender_1)#測試用
            # print(gender_1)
            line_bot_api.reply_message(event.reply_token, [FlexMessage.ask_location()])
    if postback_data=="需要幫助" :
        reply_array=[]
        reply_array.append(ImageSendMessage(original_content_url='https://imgur.com/8AKsigL.png',preview_image_url='https://imgur.com/8AKsigL.png'))
        reply_array.append(ImageSendMessage(original_content_url='https://imgur.com/bXnZJLP.png',preview_image_url='https://imgur.com/bXnZJLP.png'))
        reply_array.append(ImageSendMessage(original_content_url='https://imgur.com/QXc788f.png',preview_image_url='https://imgur.com/QXc788f.png'))
        reply_array.append(ImageSendMessage(original_content_url='https://imgur.com/BwqfFxs.png',preview_image_url='https://imgur.com/BwqfFxs.png'))
        line_bot_api.reply_message(event.reply_token,reply_array)
if __name__ == "__main__":
    app.run()