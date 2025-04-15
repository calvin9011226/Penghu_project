import logging
from datetime import datetime
import os
import json
import time
import matplotlib.pyplot as plt
import re
from collections import defaultdict

# 建立全域 logger
logger = logging.getLogger("StaticLogger")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

if not os.path.exists("documentary"):
    os.mkdir("documentary") 

#讓plt可以顯示中文
plt.rcParams["font.family"] = "DFKai-SB"  
plt.rcParams["axes.unicode_minus"] = False    


# 定義 Log 類別
class Log:
    def __init__(self, choose=["all"], Print_Funct="all", Auto_Clear=False , File_Only=False, File_Name="log"):
        # 把允許寫入 log 的方法存在 config 中 choose[all,log,data_size,data_time,data_message,data_content,else_info]
        self._config = set(choose)
        self.Print_funct = Print_Funct

        #設定是否要依照時間存取還是直接存在一個檔案
        if(File_Only):
            log_filename=f"{File_Name}.log"
        else:
            # 設定 log 檔名（以年月日_小時）格式
            now = datetime.now().strftime("%Y%m%d_%H")
            log_filename = f"./documentary/log_{now}.log"

        #設定是否要複寫還是繼續接著寫
        if(Auto_Clear):
            handler = logging.FileHandler(log_filename, mode='w')
        else:
            handler = logging.FileHandler(log_filename)

        handler.setFormatter(formatter)
        logger.addHandler(handler)


    # 決定資料是否顯示在終端機
    def print_level_handle(self,level,text):
        if self.Print_funct =="all":
            print(text)
        elif self.Print_funct =="info":
            if level=="info":
                print(text)
        
    #   data:大小  ,data_type:資料的類別   ,message:是哪個資料流的大小
    def data_size(self, data, message="", data_type="",root_config_enable=False):
        if "all" in self._config or "log" in self._config or root_config_enable or "data_size" in self._config:
            
            if data_type!="":
                data_type=f"[{data_type}]"

            logger.info(f"[Data Size] {data_type} {message} : {data}")
            self.print_level_handle("info",f"data_size 寫入->\t{data_type} {message} : {data}")

    #   data:時間  ,unit:時間單位(預設為微秒)  ,message:是哪個資料流的時間
    def data_time(self, data, message="", unit="ms",root_config_enable=False):                 
        if "all" in self._config or "log" in self._config or root_config_enable or "data_time" in self._config:
            logger.info(f"[Data Time]  {message} : {data}{unit}")
            self.print_level_handle("info",f"data_size 寫入->\t{message} : {data}{unit}")

    def data_message(self,message):
        if "all" in self._config or "log" in self._config or "data_message" in self._config:
            logger.info(message)
            self.print_level_handle("info",f"message 寫入->\t{message}")
    
    def data_content(self,data,num_limit=None):
        if "all" in self._config or "log" in self._config or "data_content" in self._config:
            if num_limit!=None and isinstance(num_limit,int):
                data=data[:num_limit]
            logger.info(data)
            self.print_level_handle("info",f"content 寫入->\t{data}")

    def else_info(self, data):
        if "all" in self._config or "log" in self._config or "else_info" in self._config:
            logger.info(f"else_info: {data}")
            self.print_level_handle("info",f"else info 寫入->\t{data}")






class CodeTimer:
    def __init__(self):
        self.start_times = {}
        self.records = [] 
    def start(self, tag):
        
        self.start_times[tag] = time.perf_counter()
        
    def stop(self, tag, size=None):
        if tag in self.start_times:
            end = time.perf_counter()
            elapsed = end - self.start_times[tag]
            self.records.append({
                'tag': tag,
                'start': self.start_times[tag],
                'end': end,
                'duration': elapsed,
                'size': size
            })
            return elapsed
        else:
            print("!!! 未建立 starttime 節點標籤")
            return None
    
    def generate_timeline_plot(records, file_name=""):
        if not records:
            print("❗ 沒有任何時間紀錄")
            return 
        
        if file_name=="":
            now = datetime.now().strftime("%Y%m%d_%H")
            save_path = f"./documentary/timeline_{now}.png"
        else:
            save_path = f"./documentary/timeline_{file_name}.png"

        fig, ax = plt.subplots(figsize=(10, len(records) * 0.5))
        for i, rec in enumerate(records):
            start = rec['start'] - records[0]['start']      #以第一個觸發時間為主
            end = rec['end'] - records[0]['start']
            duration = rec['duration']
            label = f"{rec['tag']} ({duration:.2f}s)"

            ax.broken_barh([(start, duration)], (i - 0.4, 0.4), facecolors='skyblue')
            ax.text(end + 0.1, i, f"{rec.get('size', '')}B", va='center', fontsize=8)
            # 加在 bar 中央偏下顯示 duration 時間
            ax.text(start + duration / 2, i - 0.3, f"{duration:.3f}s", ha='center', va='center', fontsize=8, color='black')
        ax.set_yticks(range(len(records)))
        ax.set_yticklabels([rec['tag'] for rec in records])
        ax.set_xlabel("Time (s)")
        ax.set_title("系統時序圖：處理階段耗時與資料大小")
        ax.grid(True, axis='x')
        plt.tight_layout()
        plt.savefig(save_path)
        print(f"✅ 已產生時序圖：{save_path}")
    
 
    def Function_duration(log_name="",file_name=""):
        if log_name=="":
            now = datetime.now().strftime("%Y%m%d_%H")
            log_path = f"./documentary/log_{now}.log"
        else:
            log_path = f"./documentary/{log_name}.log"
        
        if not os.path.exists(log_path):
            print(f"❗ 不存在{log_path}")
            return
        

        if file_name=="":
            now = datetime.now().strftime("%Y%m%d_%H")
            save_path = f"./documentary/function_time_{now}.png"
        else:
            save_path = f"./documentary/{file_name}.png"


        # 定義功能對應表
        feature_mapping = {
            "永續觀光": "景點推薦",
            "一般景點推薦": "景點推薦",
            "景點推薦": "景點推薦",
            "景點人潮": "景點人潮",
            "附近搜尋": "附近搜尋",
            "餐廳": "附近搜尋",
            "風景區": "附近搜尋",
            "停車場": "附近搜尋",
            "住宿": "附近搜尋",
            "行程規劃": "行程規劃",
            "兩天一夜": "行程規劃",
            "三天兩夜": "行程規劃",
            "四天三夜": "行程規劃",
            "五天四夜": "行程規劃",
            "收集資料&修改資料": "收集資料&修改資料",
            "年齡設定": "收集資料&修改資料",
            "性別設定": "收集資料&修改資料",
            "location": "收集資料&修改資料",
            "男": "收集資料&修改資料",
            "女": "收集資料&修改資料",
            "其他":"收集資料&修改資料",
            "租車":"租車"
        }

        # 初始化加總器
        time_summary = defaultdict(float)


        # 讀取 log 檔
        with open(log_path, "r", encoding='big5', errors='replace') as f:
            for line in f:
                if "[Data Time]" in line:
                    match = re.search(r"\[Data Time\]\s+(.*?)\s+:\s+([\d.]+)", line)
                    if match:
                        tag = match.group(1).strip()
                        ms = float(match.group(2))
                        if tag.isdigit():
                            main_tag = "收集資料&修改資料"
                        else:
                            main_tag = feature_mapping.get(tag, "其他")
                        time_summary[main_tag] += ms


        # 顯示結果（依照總時間排序）
        print("📊 各大功能總耗時（毫秒）")
        fig, ax = plt.subplots(figsize=(10, 6 * 0.5))

        sorted_items = sorted(time_summary.items(), key=lambda x: x[1], reverse=True)
        labels = [item[0] for item in sorted_items]
        values = [item[1] for item in sorted_items]

        for feature, total_s in sorted_items:
            print(f"{feature:<20} {total_s:.3f} ms")
            
            

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.barh(range(len(labels)), values, color='skyblue')
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels)
        ax.set_xlabel("Time (s)")
        ax.set_title("各項功能的總耗時")
        ax.grid(True, axis='x')
        plt.tight_layout()
        plt.savefig(save_path)





class Analyze:
    def analyze_input(data):
        # 嘗試是 JSON 字串
        if isinstance(data, str):
            try:
                parsed = json.loads(data)
                print("✅ 這是 JSON 字串")
                return "json", len(data.encode('utf-8'))
            except json.JSONDecodeError:
                print("✅ 這是純文字")
                return "text", len(data.encode('utf-8'))

        elif isinstance(data, dict) or isinstance(data, list):
            print("✅ 這是已解析的 JSON 結構")
            return "json_dict", len(str(data).encode('utf-8'))

        elif isinstance(data, bytes):
            print("✅ 這是二進制資料")
            return "binary", len(data)

        else:
            print("❓ 無法辨識")
            return "unknown", len(str(data).encode('utf-8'))
        
    import matplotlib.pyplot as plt






# === Helper function for快速結束並記錄 === (結合log時間、大小紀錄 + 時間序) 
def timer_stop_log(tag,size=None, content="", timer=None, log=None):
    """
    自動停止計時並記錄耗時與資料大小

    :param tag: 記錄的標籤名稱
    :param content: 要分析大小的資料
    :param timer: CodeTimer 實例
    :param log: Log 實例
    """

    if timer is None or log is None:
        print("❗請傳入 timer 與 log 實例")
        return
    if size==None:
        size_content=len(str(content).encode('utf-8'))
    else:
        size_content=size
    elapsed = timer.stop(tag, size=size_content)
    log.data_time(elapsed, message=tag,root_config_enable=True)
    log.data_size(size_content, message=tag,root_config_enable=True)
        




