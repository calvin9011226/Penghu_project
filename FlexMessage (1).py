from flask import Flask, request
from random import randrange
import json
import os
import pandas as pd
import numpy as np
import csv
from linebot import LineBotApi, WebhookHandler
from linebot.models.events import PostbackEvent
from linebot.models import *
import Search
import urllib.parse
import googlemaps
access_token = os.getenv("LINE_ACCESS_TOKEN")
secret = os.getenv("LINE_CHANNEL_SECRET")
line_bot_api = LineBotApi(access_token)  # 確認 token 是否正確
handler = WebhookHandler(secret)         # 確認 secret 是否正確

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


# 新增全域變數 option2，用來記錄使用者選擇的路線類型
option2 = None

def ask_route_option():
    """建立 Flex Message 讓使用者選擇『系統路線』或『使用者路線』"""
    bubble = BubbleContainer(
        direction="ltr",
        body=BoxComponent(
            layout="vertical",
            contents=[
                TextComponent(text="請選擇您要的路線", size="xl", color="#000000", align="center")
            ]
        ),
        footer=BoxComponent(
            layout="vertical",
            spacing="xs",
            contents=[
                ButtonComponent(
                    style="primary",
                    action=PostbackAction(label="系統路線", text="系統路線", data="系統路線")
                ),
                ButtonComponent(
                    style="primary",
                    action=PostbackAction(label="使用者路線", text="使用者路線", data="使用者路線")
                )
            ]
        )
    )
    return FlexSendMessage(alt_text="選擇路線", contents=bubble)

# ----------------------------
# 詢問旅遊天數
def travel_reply(Title, label1, text1, data1, label2, text2, data2, label3, text3, data3, label4, text4, data4):
    body = request.get_data(as_text=True)
    try:
        json_data = json.loads(body)
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)
        tk = json_data['events'][0]['replyToken']
        
        bubble = BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url='https://i.imgur.com/o2S08In.png',
                size='full',
                aspect_ratio='2:1',
                aspect_mode='cover'
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text="請選擇您的行程規劃天數", size='xl', color='#000000')
                ]
            ),
            footer=BoxComponent(
                layout='vertical',
                spacing='xs',
                contents=[
                    ButtonComponent(
                        style='secondary',
                        color='#FFEE99',
                        height='sm',
                        action=PostbackAction(label=label1, text=text1, data=data1)
                    ),
                    SeparatorComponent(color='#000000'),
                    ButtonComponent(
                        style='secondary',
                        color='#FFEE99',
                        height='sm',
                        action=PostbackAction(label=label2, text=text2, data=data2)
                    ),
                    SeparatorComponent(color='#000000'),
                    ButtonComponent(
                        style='secondary',
                        color='#FFEE99',
                        height='sm',
                        action=PostbackAction(label=label3, text=text3, data=data3)
                    ),
                    SeparatorComponent(color='#000000'),
                    ButtonComponent(
                        style='secondary',
                        color='#FFEE99',
                        height='sm',
                        action=PostbackAction(label=label4, text=text4, data=data4)
                    )
                ]
            )
        )
        message = FlexSendMessage(alt_text=Title, contents=bubble)
        return message
    except Exception as e:
        print("travel_reply error:", e)
        line_bot_api.reply_message(tk, TextSendMessage(text="發生錯誤"))

# ----------------------------
# 訊問是否要繼續
def ask_continue():
    body = request.get_data(as_text=True)
    try:
        json_data = json.loads(body)
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)
        tk = json_data['events'][0]['replyToken']
        
        bubble = BubbleContainer(
            direction='ltr',
            body=BoxComponent(
                layout='horizontal',
                contents=[
                    TextComponent(text="是否繼續查詢", size='xl', color='#4C0099', align="center")
                ]
            ),
            footer=BoxComponent(
                layout='horizontal',
                spacing='xs',
                contents=[
                    ButtonComponent(
                        style='secondary',
                        color='#FFEE99',
                        height='sm',
                        action=PostbackAction(label="是，請繼續", text="是，請繼續", data="是，請繼續")
                    )
                ]
            )
        )
        message = FlexSendMessage(alt_text="是否繼續", contents=bubble)
        return message
    except Exception as e:
        print("ask_continue error:", e)
        line_bot_api.reply_message(tk, TextSendMessage(text="發生錯誤"))

# ----------------------------
# 請求傳送位置資訊
def ask_location():
    body = request.get_data(as_text=True)
    try:
        json_data = json.loads(body)
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)
        tk = json_data['events'][0]['replyToken']
        
        bubble = BubbleContainer(
            direction='ltr',
            body=BoxComponent(
                layout='horizontal',
                contents=[
                    TextComponent(text="請告訴系統您目前的位置", size='xl', color='#4C0099', align="center")
                ]
            ),
            footer=BoxComponent(
                layout='horizontal',
                spacing='xs',
                contents=[
                    BoxComponent(
                        layout='horizontal',
                        spacing='xs',
                        contents=[
                            ButtonComponent(
                                style='secondary',
                                color='#FFEE99',
                                height='sm',
                                action=PostbackAction(label="需要幫助", text="需要幫助", data="需要幫助")
                            ),
                            ButtonComponent(
                                style='secondary',
                                color='#FFEE99',
                                height='sm',
                                action=PostbackAction(label="好", text="好", data="好")
                            )
                        ]
                    )
                ]
            )
        )
        message = FlexSendMessage(alt_text="請傳送位置資訊", contents=bubble)
        # 加入 Quick Reply 按鈕，使用 LocationAction 讓使用者傳送位置
        message.quick_reply = QuickReply(
            items=[
                QuickReplyButton(
                    action=LocationAction(label="傳送位置")
                )
            ]
        )
        return message
    except Exception as e:
        print("ask_location error:", e)
        line_bot_api.reply_message(tk, TextSendMessage(text="發生錯誤"))


# ----------------------------
# 訊問關鍵字
def ask_keyword():
    body = request.get_data(as_text=True)
    try:
        json_data = json.loads(body)
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)
        tk = json_data['events'][0]['replyToken']
        
        bubble = BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url='https://zh-tw.skyticket.com/guide/wp-content/uploads/2020/12/shutterstock_1086233933.jpg',
                align="center",
                size='full',
                aspect_ratio='20:15',
                aspect_mode='cover'
            ),
            body=BoxComponent(
                layout='horizontal',
                contents=[
                    TextComponent(text="請選擇搜尋的關鍵字", size='xl', color='#4C0099', align="center")
                ]
            ),
            footer=BoxComponent(
                layout='vertical',
                spacing='xs',
                contents=[
                    BoxComponent(
                        layout='vertical',
                        spacing='xs',
                        contents=[
                            BoxComponent(
                                layout='horizontal',
                                spacing='xs',
                                contents=[
                                    BoxComponent(
                                        layout='vertical',
                                        spacing='xs',
                                        contents=[
                                            ImageComponent(
                                                url="https://th.bing.com/th/id/OIP.bz7UqgUAkIQZ_l5BA8WQ0AHaHa?pid=ImgDet&w=512&h=512&rs=1",
                                                aspectRatio="1:1",
                                                aspectMode="cover",
                                                size="md"
                                            ),
                                            ButtonComponent(
                                                style='secondary',
                                                color='#FFEE99',
                                                height='sm',
                                                action=MessageAction(label="風景區", text="風景區")
                                            )
                                        ]
                                    ),
                                    BoxComponent(
                                        layout='vertical',
                                        spacing='xs',
                                        contents=[
                                            ImageComponent(
                                                url="https://thumb.silhouette-ac.com/t/d8/d8a7e9674d55ca5fe9173b02cc4fb7dd_w.jpeg",
                                                aspectRatio="1:1",
                                                aspectMode="cover",
                                                size="md"
                                            ),
                                            ButtonComponent(
                                                style='secondary',
                                                color='#FFEE99',
                                                height='sm',
                                                action=MessageAction(label="餐廳", text="餐廳")
                                            )
                                        ]
                                    )
                                ]
                            ),
                            BoxComponent(
                                layout='horizontal',
                                spacing='xs',
                                contents=[
                                    BoxComponent(
                                        layout='vertical',
                                        spacing='xs',
                                        contents=[
                                            ImageComponent(
                                                url="https://th.bing.com/th/id/OIP.VgsoPsjpE4Pb9BRWjZ5tFwAAAA?pid=ImgDet&rs=1",
                                                aspectRatio="1:1",
                                                aspectMode="cover",
                                                size="md"
                                            ),
                                            ButtonComponent(
                                                style='secondary',
                                                color='#FFEE99',
                                                height='sm',
                                                action=MessageAction(label="停車場", text="停車場")
                                            )
                                        ]
                                    ),
                                    BoxComponent(
                                        layout='vertical',
                                        spacing='xs',
                                        contents=[
                                            ImageComponent(
                                                url="https://png.pngtree.com/png-vector/20190623/ourlarge/pngtree-hotel-icon-png-image_1511479.jpg",
                                                aspectRatio="1:1",
                                                aspectMode="cover",
                                                size="md"
                                            ),
                                            ButtonComponent(
                                                style='secondary',
                                                color='#FFEE99',
                                                height='sm',
                                                action=MessageAction(label="住宿", text="住宿")
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        )
        message = FlexSendMessage(alt_text="選擇關鍵字", contents=bubble)
        return message
    except Exception as e:
        print(f"ask_keyword 發生錯誤: {e}")
        line_bot_api.reply_message(tk, TextSendMessage(text="發生錯誤，請稍後再試"))

def get_price_level_from_google(place_id):
    #GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    if not GOOGLE_API_KEY:
        print("❌ 尚未設定 GOOGLE_API_KEY，無法查詢 price_level")
        return None

    gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
    ''''''
    try:
        response = gmaps.place(place_id=place_id, language='zh-TW')
        # 印出完整的 JSON 回傳內容，方便除錯
        #print("完整回傳 JSON:", response)
        if 'result' in response and 'price_level' in response['result']:
            return response['result']['price_level']
        else:
            return None
    except Exception as e:
        print(f"❌ 呼叫 Google Place Details 失敗: {e}")
        return None


# ----------------------------
# 店家資訊（加入平均價格顯示）
def recommend(name, rating, img_url, location, place_id, google_price_level=None, average_price=None):
    """
    產生推薦店家資訊的 FlexMessage，price_level 改成由 google_price_level 取得。
    """
    body = request.get_data(as_text=True)
    component = Rating_Component(rating)

    # Google price_level 對應文字
    price_mapping = {
        0: "免費",
        1: "低價位",
        2: "中等價位",
        3: "較高價位",
        4: "高價位"
    }

    try:
        # ★ 若 google_price_level 有抓到，就用它；否則顯示 "無價格資訊"
        if google_price_level is not None:
            price_text = price_mapping.get(google_price_level, "無價格資訊")
        else:
            price_text = "無價格資訊"

        # 若有平均價格，就補上 (約NT$xxx)
        if average_price is not None:
            try:
                avg = float(average_price)
                avg_text = f" (約 NT${int(avg)})"
            except:
                avg_text = ""
        else:
            avg_text = ""

        price_info = price_text + avg_text

        # 解析 location
        if isinstance(location, dict):
            lat, lng = location.get('lat', 0), location.get('lng', 0)
        else:
            # 嘗試把 JSON 字串轉成 dict
            try:
                loc_dict = json.loads(location)
                lat, lng = loc_dict.get('lat', 0), loc_dict.get('lng', 0)
            except:
                lat, lng = 0, 0

        # 產生 Google Maps URL
        name_encoded = urllib.parse.quote(name, safe='')
        if place_id and place_id.strip().lower() != "no information":
            maps_url = f"https://www.google.com/maps/search/?api=1&query={name_encoded}&query_place_id={place_id}"
        else:
            maps_url = f"https://www.google.com/maps/search/?api=1&query={name_encoded}+{lat},{lng}"

        json_data = json.loads(body)
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)
        tk = json_data['events'][0]['replyToken']

        bubble = BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url=img_url,
                align="center",
                size='full',
                aspect_ratio='20:15',
                aspect_mode='cover'
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text=name, size='xl', color='#000000'),
                    BoxComponent(
                        layout='baseline',
                        margin='md',
                        contents=component
                    ),
                    # ★ 這裡的 price_info 就是從 Google 動態拿到的 price_level
                    TextComponent(text=f"價格等級: {price_info}", size='md', color='#000000')
                ]
            ),
            footer=BoxComponent(
                layout='vertical',
                spacing='xs',
                contents=[
                    ButtonComponent(
                        style='secondary',
                        color='#FFEE99',
                        height='sm',
                        action=URIAction(
                            label='查看地圖',
                            uri=maps_url
                        )
                    )
                ]
            )
        )

        message = FlexSendMessage(alt_text=name, contents=bubble)
        return bubble

    except Exception as e:
        print("❌ 建立 FlexMessage 時發生錯誤:", e)
        line_bot_api.reply_message(tk, TextSendMessage(text="發生錯誤"))
        return None

# ----------------------------
# 星等
def Rating_Component(rating):
    rating = float(rating)
    rating_str = str(rating)
    integer_part, decimal_part = rating_str.split('.')
    integer_part = int(integer_part)
    decimal_part = int(decimal_part)
    component = []
    for _ in range(integer_part):
        icon_component = IconComponent(
            size='sm',
            url="https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
        )
        component.append(icon_component)
    if integer_part == 0:
        integer_part = 1
    if integer_part < 5:
        if decimal_part < 4:
            icon_component = IconComponent(
                size='sm',
                url="https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gray_star_28.png"
            )
            component.append(icon_component)
        elif 3 < decimal_part < 8:
            icon_component = IconComponent(
                size='sm',
                url="https://i.imgur.com/8eAZJ80.png"
            )
            component.append(icon_component)
        else:
            icon_component = IconComponent(
                size='sm',
                url="https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
            )
            component.append(icon_component)
        integer_part = integer_part + 1
    if integer_part < 5:
        for _ in range(5 - integer_part):
            icon_component = IconComponent(
                size='sm',
                url="https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gray_star_28.png"
            )
            component.append(icon_component)
    text_component = TextComponent(
        text=rating_str,
        size='sm',
        color="#999999",
        margin="md",
        flex=0
    )
    component.append(text_component)
    return component

# ----------------------------
# 很多店家資訊
def Carousel(carousel_contents):
    body = request.get_data(as_text=True)
    try:
        json_data = json.loads(body)
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)
        tk = json_data['events'][0]['replyToken']
        carousel_flex_message = CarouselContainer(contents=carousel_contents)
        message = FlexSendMessage(alt_text='店家資訊', contents=carousel_flex_message)
        return message
    except:
         line_bot_api.reply_message(tk, TextSendMessage(text="發生錯誤"))

# ----------------------------
# 將 CSV 檔案內資料轉成 Carousel 內容
def Carousel_contents(file):
    with open(file, mode='r', newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader)  # 跳過標題行
        carousel_contents = []
        rows = list(reader)
        n = min(10, len(rows))  # 只顯示最多10筆
        i = 1

        for row in rows:
            try:
                name = row[0]       # 店名
                rating = row[2]     # 評分
                img_url = row[3]    # 圖片
                location = row[4]   # 位置信息（JSON字串或其他）
                place_id = row[5]   # Google Place ID

                # ★ 改成從 Google 拿 price_level，而不是用 CSV 裡的 row[1]
               

                google_price_level = get_price_level_from_google(place_id )

                # 若有第 6 欄位是平均價格，可酌情保留
                average_price = row[6] if len(row) > 6 else None

                # 呼叫 recommend()，把我們抓到的 google_price_level 帶進去
                bubble = recommend(
                    name=name,
                    rating=rating,
                    img_url=img_url,
                    location=location,
                    place_id=place_id,
                    google_price_level=google_price_level,
                    average_price=average_price
                )

                if bubble:
                    carousel_contents.append(bubble)
                if i == n:
                    break
                i += 1
            except Exception as e:
                print(f"❌ 建立 Bubble 時發生錯誤: {e}")
    return carousel_contents
# ----------------------------
# 詢問要在哪裡找尋飯店
def Plan_hotel(Plan_contents):
    body = request.get_data(as_text=True)
    try:
        json_data = json.loads(body)
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)
        tk = json_data['events'][0]['replyToken']
        
        bubble = BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url='https://th.bing.com/th/id/R.93316e4363d28d99e9ecd8debc5e57de?rik=hhiGLzuuawAWsQ&pid=ImgRaw&r=0',
                size='full',
                aspect_ratio='2:1',
                aspect_mode='cover'
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text="您要在哪個景點搜尋民宿", size='xl', color='#000000')
                ]
            ),
            footer=BoxComponent(
                layout='vertical',
                spacing='xs',
                contents=Plan_contents
            )
        )
        message = FlexSendMessage(alt_text="選擇景點", contents=bubble)
        return message
    except:
         line_bot_api.reply_message(tk, TextSendMessage(text="發生錯誤"))

def Plan_contents(file):  
    with open(file, mode='r', newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader)  # 跳過標頭行
        plan_contents = []
        rows = list(reader)
        n = min(10, len(rows))
        i = 1
        for row in rows:
            contents = ButtonComponent(
                        style='secondary',
                        color='#FFEE99',
                        height='sm',
                        action=TextSendMessage(label=row[4], text=row[4])
                    ) 
            plan_contents.append(contents)
            if i == n:
                break
            i += 1
    return plan_contents

def gender_reply(Title, question, label1, text1, data1, label2, text2, data2, label3, text3, data3):
    try:
        bubble = BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                    url="https://th.bing.com/th/id/R.c0c0ea7da18a703a414e22914b4b7ad3?rik=79Ben6v2hTid9A&pid=ImgRaw&r=0",
                    size='full',
                    aspect_ratio='20:13',
                    aspect_mode='cover'
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text=question, size='xl', color='#000000', align='center')
                ]
            ),
            footer=BoxComponent(
                layout='vertical',
                spacing='xs', 
                contents=[
                    ButtonComponent(
                        style='secondary',
                        color='#FFEE99',
                        height='sm',
                        action=PostbackAction(label=label1, text=text1, data=data1)
                    ),
                    SeparatorComponent(color='#000000'),
                    ButtonComponent(
                        style='secondary',
                        color='#FFEE99',
                        height='sm',
                        action=PostbackAction(label=label2, text=text2, data=data2)
                    ),
                    SeparatorComponent(color='#000000'),
                    ButtonComponent(
                        style='secondary',
                        color='#FFEE99',
                        height='sm',
                        action=PostbackAction(label=label3, text=text3, data=data3)
                    ),
                    SeparatorComponent(color='#000000')
                ]
            )
        )
        message = FlexSendMessage(alt_text=Title, contents=bubble)
        return message
    except:
        print("ERROR")
        
def classify_gender(gender):
    if gender == "男":
        return 1
    elif gender == "女":
        return 0
    elif gender == "其他":
        return -1
