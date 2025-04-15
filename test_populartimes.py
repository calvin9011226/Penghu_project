
import populartimes
import csv
api_key = "AIzaSyBkBeV2pKxDvLzQmcCe1X6jkqWMFhVXiuI"

# 設定查詢區域 (經緯度範圍)
lat_min, lat_max = 23.575, 23.58  # 只查詢更小範圍
lng_min, lng_max = 119.565, 119.57

# 嘗試獲取熱門時段數據
try:
    data = populartimes.get(api_key, [""], (lat_min, lng_min), (lat_max, lng_max))
    print(data)
except Exception as e:
    print("獲取失敗：", e)




# 設定 CSV 檔案名稱
csv_filename = "./penghu_populartimes_full.csv"

# 寫入 CSV

with open(csv_filename, mode="w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)

    # 寫入標題列
    header = ["地點", "地址", "評分", "星期", "時間 (小時)", "人潮"]
    writer.writerow(header)

    # 寫入數據
    for place in data:
        for day in place["populartimes"]:
            for hour, value in enumerate(day["data"]):
                writer.writerow([
                    place["name"], 
                    place["address"], 
                    place.get("rating", "N/A"),  # 若無評分則填 "N/A"
                    day["name"], 
                    hour, 
                    value
                ])

# 回傳 CSV 檔案路徑
csv_filename

"""
import matplotlib.pyplot as plt

# 取得樂樂家熱炒的熱門時段數據
restaurant_name = data[0]["name"]
monday_data = data[0]["populartimes"][0]["data"]
tuesday_data = data[0]["populartimes"][1]["data"]

# 畫圖
plt.figure(figsize=(10,5))
plt.plot(range(24), monday_data, marker="o", label="Monday")
plt.plot(range(24), tuesday_data, marker="o", label="Tuesday")

plt.title(f"{restaurant_name} - hot_time")
plt.xlabel("time (hours)")
plt.ylabel("people (%)")
plt.xticks(range(0, 24, 1))
plt.legend()
plt.grid()
plt.show()
"""