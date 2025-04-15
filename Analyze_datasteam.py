import logging
from datetime import datetime
import os
import json
import time
import matplotlib.pyplot as plt
import re
from collections import defaultdict
from matplotlib.patches import Patch
from matplotlib import cm

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
    VALID_PRINT_FUNCTS = {"off", "info", "all"}
    def __init__(self, choose=["all"], Print_Funct="all", Auto_Clear=False , File_Only=False, File_Name="log"):
        # 把允許寫入 log 的方法存在 config 中 choose[all,log,data_size,data_time,data_message,data_content,else_info]
        
        if logger.handlers:             #防止因為多個Log而造成產生過多的logger
            logger.handlers.clear()

        self._config = set(choose)

        if Print_Funct not in self.VALID_PRINT_FUNCTS:
            print(f"⚠️ 無效的 Print_Funct 設定：{Print_Funct}，自動改為 'off'")
            Print_Funct = "off"
        self.Print_funct = Print_Funct

        self.print_level_handle(" ",f"choose以設定:{self._config}")

        #設定是否要依照時間存取還是直接存在一個檔案
        if(File_Only):
            log_filename=f"./documentary/{File_Name}.log"
        else:
            # 設定 log 檔名（以年月日_小時）格式
            now = datetime.now().strftime("%Y%m%d_%H")
            log_filename = f"./documentary/log_{now}.log"

        #設定是否要複寫還是繼續接著寫
        if(Auto_Clear):
            handler = logging.FileHandler(log_filename, mode='w')
            self.print_level_handle(" ",f"已清空{log_filename}的檔案")
        else:
            handler = logging.FileHandler(log_filename)
            self.print_level_handle(" ",f"新增到{log_filename}的檔案")

        handler.setFormatter(formatter)
        logger.addHandler(handler)



    # 決定資料是否顯示在終端機
    def print_level_handle(self,level,text):
        
        if self.Print_funct =="all":
            print(text)
        elif self.Print_funct =="info" and level=="info":
            print(text)


    #   data:大小  ,data_type:資料的類別   ,message:是哪個資料流的大小
    def data_size(self, data, message="", data_type="",root_config_enable=False):
        if "all" in self._config or "log" in self._config or root_config_enable or "data_size" in self._config:
            
            if data_type!="":
                data_type=f"[{data_type}]"

            logger.info(f"[Data Size] {data_type} {message} : {data}")
            self.print_level_handle("info",f"data_size 寫入->\t{data_type} {message} : {data}")

    #   data:時間  ,unit:時間單位(預設為微秒)  ,message:是哪個資料流的時間
    def data_time(self, data, message="", unit="s",root_config_enable=False):                 
        if "all" in self._config or "log" in self._config or root_config_enable or "data_time" in self._config:
            logger.info(f"[Data Time]  {message} : {data:.7f}{unit}")
            self.print_level_handle("info",f"data_size 寫入->\t{message} : {data}{unit}")

    def data_message(self, message):
        if "all" in self._config or "log" in self._config or "data_message" in self._config:
            logger.info(message)
            self.print_level_handle("info",f"message 寫入->\t{message}")
    
    def data_content(self, data,num_limit=None):
        if "all" in self._config or "log" in self._config or "data_content" in self._config:
            if num_limit!=None and isinstance(num_limit,int):
                data=data[:num_limit]
            logger.info(data)
            self.print_level_handle("info",f"content 寫入->\t{data}")

    def else_info(self, data,info_type, data_type="", message="", unit=""):
        if "all" in self._config or "log" in self._config or "else_info" in self._config:
            logger.info(f"[{info_type}] {data_type} {message} : {data}{unit}")
            self.print_level_handle("info",f"else info 寫入->\t[{info_type}] {data_type} {message} : {data}{unit}")






class CodeTimer:
    
    def __init__(self,choose=["all"], Print_Funct="all"):


        self.start_times = {}
        self.records = [] 
        self._config = set(choose)
        self.Print_Funct=Print_Funct
        self.print_level_handle(" ",f"choose以設定:{self._config}")


    # 決定資料是否顯示在終端機(暫時只有all跟off)
    def print_level_handle(self,level,text):
        if self.Print_Funct =="all":
            print(text)


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
    
    def generate_timeline_plot(self, file_name="",refresh=True,size_off=False):
        if  "all" in self._config or "timeline" in self._config:
            max_records = 100
            records = self.records[:max_records]

            if not records:
                print("❗ 沒有任何時間紀錄")
                return
            
            if  len(records)>max_records:
                print("❗記錄的資料太多,只保留前100個資料❗")

            if file_name=="":
                now = datetime.now().strftime("%Y%m%d_%H")
                save_path = f"./documentary/timeline_{now}.png"
            else:
                save_path = f"./documentary/{file_name}.png"
            
            tag_records = defaultdict(list)
            for rec in records:
                tag_records[rec['tag']].append(rec)

            # 為每個 tag 分配一條 y 軸位置
            tag_y_map = {tag: i for i, tag in enumerate(tag_records.keys())}

            fig, ax = plt.subplots(figsize=(10, len(tag_y_map) * 0.6))
            for tag, rec_list in tag_records.items():
                y_pos = tag_y_map[tag]
                for rec in rec_list:
                    start = rec['start'] - records[0]['start']
                    duration = rec['duration']
                    end = rec['end'] - records[0]['start']
                    size= rec['size']
                    ax.broken_barh([(start, duration)], (y_pos - 0.2, 0.4), facecolors='skyblue')
                    ax.text(start + duration / 2, y_pos, f"{duration:.3f}s", ha='center', va='center', fontsize=8)
                    if not size_off:
                        ax.text(end+0.25 , y_pos+ 0.25, f"{size}B", ha='right', va='bottom', fontsize=8)
            ax.set_yticks(range(len(tag_y_map)))
            ax.set_yticklabels(tag_y_map.keys())
            ax.set_xlabel("Time (s)")
            if size_off:
                ax.set_title("系統時序圖：處理階段耗時")
            else:
                ax.set_title("系統時序圖：處理階段耗時與資料大小")
            ax.grid(True, axis='x')
            plt.tight_layout()
            plt.savefig(save_path)
            self.print_level_handle(" ",f"✅ 已產生時序圖{save_path}")
            if refresh:
                self.records.clear()
                self.print_level_handle(" ", "✅ records 已清空")
        else:
            print("!!! 未啟動 generate_timeline_plot !!!")
            return

    def Function_duration(self, log_name="", file_name="", feature_mapping=None, size_off=False, detail_timestamp=False):
        if "all" in self._config or "Function_duration" in self._config:

            # 1. 設定 log 檔路徑
            if log_name == "":
                now = datetime.now().strftime("%Y%m%d_%H")
                log_path = f"./documentary/log_{now}.log"
            else:
                log_path = f"./documentary/{log_name}.log"
            
            if not os.path.exists(log_path):
                print(f"❗ 不存在 {log_path}")
                return
            else:
                self.print_level_handle(" ", f"分析: {log_path}")

            # 2. 設定存圖路徑
            if file_name == "":
                now = datetime.now().strftime("%Y%m%d_%H")
                save_path = f"./documentary/function_time_{now}.png"
            else:
                save_path = f"./documentary/{file_name}.png"

            # 3. 預設功能對應表
            if feature_mapping is None:
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
                    "其他": "收集資料&修改資料",
                    "租車": "租車"
                }

            # 4. 累計統計數據
            time_summary = defaultdict(float)        # 大功能 → 累計耗時
            size_summary = defaultdict(int)          # 大功能 → 累計資料大小
            sub_time_summary = defaultdict(lambda: defaultdict(float))  # 大功能 → {子功能: 累計耗時}
            
            import re
            with open(log_path, "r", encoding='big5', errors='replace') as f:
                for line in f:
                    if "[Data Time]" in line:
                        match = re.search(r"\[Data Time\]\s+(.*?)\s+:\s+([\d.]+)", line)
                        if match:
                            tag = match.group(1).strip()
                            used_time = float(match.group(2))
                            if tag.isdigit():
                                main_tag = "收集資料&修改資料"
                            else:
                                main_tag = feature_mapping.get(tag, "其他")
                            time_summary[main_tag] += used_time
                            sub_time_summary[main_tag][tag] += used_time
                    if (not size_off) and ("[Data Size]" in line):
                        match = re.search(r"\[Data Size\]\s+(.*?)\s+:\s+([\d.]+)", line)
                        if match:
                            tag = match.group(1).strip()
                            data_size = float(match.group(2))
                            if tag.isdigit():
                                main_tag = "收集資料&修改資料"
                            else:
                                main_tag = feature_mapping.get(tag, "其他")
                            size_summary[main_tag] += data_size

            # 印出統計數據
            print("📊 各大功能總耗時（秒）")
            sorted_time = sorted(time_summary.items(), key=lambda x: x[1], reverse=True)
            for feat, t in sorted_time:
                if not size_off:
                    sz = size_summary.get(feat, 0)
                    print(f"{feat:<15} {t:.4f}s | 資料大小: {int(sz)}B")
                else:
                    print(f"{feat:<15} {t:.4f}s")
            
            # 5. 根據 detail_timestamp 決定圖形模式
            if detail_timestamp:
                # 詳細模式：堆疊式水平長條圖
                
                # 5-1. 計算每個大功能的總耗時（排序用）
               
                total_time = {big: sum(sub_time_summary[big].values()) for big in sub_time_summary}
                sorted_big = sorted(total_time.items(), key=lambda x: x[1], reverse=True)

                # 5-2. 準備大功能與子功能數據
                big_labels = []
                big_values = []        # 每項為子功能耗時列表
                big_sublabels = []     # 每項為子功能名稱列表
                for big, _ in sorted_big:
                    big_labels.append(big)
                    sorted_sub = sorted(sub_time_summary[big].items(), key=lambda x: x[1], reverse=True)
                    sub_times = [x[1] for x in sorted_sub]
                    sub_tags = [x[0] for x in sorted_sub]
                    big_values.append(sub_times)
                    big_sublabels.append(sub_tags)

                # 5-3. 將所有子功能放到一起，全域分配顏色
                all_subfeatures = set()
                for sub_list in big_sublabels:
                    all_subfeatures.update(sub_list)
                all_subfeatures = sorted(all_subfeatures)
                # 利用 matplotlib 的 tab20 colormap 自動分配固定色

                total_sub = len(all_subfeatures)
                cmap_all = cm.get_cmap("tab20", total_sub)
                sub_color_global = {sub: cmap_all(i) for i, sub in enumerate(all_subfeatures)}

                # 5-4. 為每個大功能下的子功能，從全域 mapping 中取顏色
                big_bar_colors = []
                for sub_tags in big_sublabels:
                    colors = [sub_color_global.get(sub, "#9E9E9E") for sub in sub_tags]
                    big_bar_colors.append(colors)

                # 5-5. 畫出堆疊圖
                fig, ax = plt.subplots(figsize=(10, len(big_labels)*0.8))
                for i, (sub_times, colors, sub_tags) in enumerate(zip(big_values, big_bar_colors, big_sublabels)):
                    left = 0
                    for time_val, color, sub_tag in zip(sub_times, colors, sub_tags):
                        ax.barh(i, time_val, left=left, color=color, edgecolor="white")
                        ax.text(left + time_val/2, i, f"{time_val:.2f}s", ha="center", va="center", fontsize=8, color="white")
                        left += time_val

                ax.set_yticks(range(len(big_labels)))
                ax.set_yticklabels(big_labels)
                ax.set_xlabel("Time (s)")
                ax.set_title("各項功能總耗時與資料大小")
                ax.grid(True, axis="x")
                # Legend：使用全域子功能顏色 mapping

                legend_handles = [Patch(color=sub_color_global[sub], label=sub) for sub in all_subfeatures]
                ax.legend(handles=legend_handles, title="訊息或子功能", loc='center left',bbox_to_anchor=(1.02, 0.5), borderaxespad=0.,ncol=1 )
            
            else:
                # 簡單模式：僅顯示各大功能總耗時
                sorted_items = sorted(time_summary.items(), key=lambda x: x[1], reverse=True)
                labels = [item[0] for item in sorted_items]
                values = [item[1] for item in sorted_items]
                # 這裡以預設 colormap 自動分配顏色（例如 tab10）
                cmap_simple = plt.get_cmap("tab10", len(labels))
                bar_colors = [cmap_simple(i) for i in range(len(labels))]
                
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.barh(range(len(labels)), values, color=bar_colors)
                if not size_off:
                    for i, feat in enumerate(labels):
                        sz = size_summary.get(feat, 0)
                        ax.text(values[i], i, f"{int(sz)}B", va="center", fontsize=8)
                    ax.set_title("各項功能總耗時與資料大小")
                else:
                    ax.set_title("各項功能總耗時")
                ax.set_yticks(range(len(labels)))
                ax.set_yticklabels(labels)
                ax.set_xlabel("Time (s)")
                ax.grid(True, axis="x")
            
            plt.tight_layout()
            plt.savefig(save_path)
            self.print_level_handle("info", f"✅ 已產生圖 {save_path}")
        else:
            print("!!! 未啟動 Function_duration !!!")
            return


        
"""
    def Function_duration(self,log_name="",file_name="",feature_mapping=None,size_off=False):
        if  "all" in self._config or "Function_duration" in self._config:
            if log_name=="":
                now = datetime.now().strftime("%Y%m%d_%H")
                log_path = f"./documentary/log_{now}.log"
            else:
                log_path = f"./documentary/{log_name}.log"
            

            if not os.path.exists(log_path):
                print(f"❗ 不存在{log_path}")
                return
            else:
                self.print_level_handle(" ",f"分析:{log_path}")

            if file_name=="":
                now = datetime.now().strftime("%Y%m%d_%H")
                save_path = f"./documentary/function_time_{now}.png"
            else:
                save_path = f"./documentary/{file_name}.png"

            if feature_mapping == None:
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
                color_map = {
                    # 收集資料子項目
                    "男": "#F44336",
                    "女": "#E91E63",
                    "年齡設定": "#FF9800",
                    "location": "#FFC107",

                    # 行程規劃子項目
                    "行程規劃": "#4CAF50",
                    "兩天一夜": "#66BB6A",
                    "三天兩夜": "#81C784",

                    # 景點推薦
                    "永續觀光": "#2196F3",
                    "一般景點推薦": "#42A5F5",
                    "景點推薦": "#64B5F6",

                    # 景點人潮
                    "景點人潮": "#9C27B0",

                    # 附近搜尋
                    "附近搜尋": "#FF5722",
                    "風景區": "#FF7043",
                    "停車場": "#FF8A65",
                    "餐廳": "#FFAB91",
                    "住宿": "#FFCCBC",

                    # 租車
                    "租車": "#009688",

                    # fallback
                    "其他": "#9E9E9E"
                }

            
            

            # 初始化加總器
            time_summary = defaultdict(float)
            size_summary = defaultdict(int)

            # 讀取 log 檔
            with open(log_path, "r", encoding='big5', errors='replace') as f:
                for line in f:
                    if "[Data Time]" in line:
                        match = re.search(r"\[Data Time\]\s+(.*?)\s+:\s+([\d.]+)", line)
                        if match:
                            tag = match.group(1).strip()
                            s = float(match.group(2))
                            if tag.isdigit():
                                main_tag = "收集資料&修改資料"
                            else:
                                main_tag = feature_mapping.get(tag, "其他")
                            time_summary[main_tag] += s
                    if (not size_off) and ("[Data Size]" in line) :
                        match = re.search(r"\[Data Size\]\s+(.*?)\s+:\s+([\d.]+)", line)
                        if match:
                            tag = match.group(1).strip()
                            size = float(match.group(2))
                            if tag.isdigit():
                                main_tag = "收集資料&修改資料"
                            else:
                                main_tag = feature_mapping.get(tag, "其他")
                            size_summary[main_tag] += size


            # 顯示結果（依照總時間排序）
            print("📊 各大功能總耗時（毫秒）")
            fig, ax = plt.subplots(figsize=(10, 6 * 0.5))

            sorted_items = sorted(time_summary.items(), key=lambda x: x[1], reverse=True)
            sorted_items_size = sorted(size_summary.items(), key=lambda x: x[1], reverse=True)
            labels = [item[0] for item in sorted_items]
            values = [item[1] for item in sorted_items]
            bar_colors = [color_map.get(label, "#9E9E9E") for label in labels]

            for feature, total_s in sorted_items:
                print(f"{feature:<15} {total_s:.4f} s",end="")
                if not size_off:
                    size = size_summary.get(feature, 0)
                    print(f" ⮕ 資料總大小：{int(size)} B")
                



            fig, ax = plt.subplots(figsize=(10, 5))
            #ax.barh(range(len(labels)), values, color='skyblue')
            ax.barh(range(len(labels)), values, color=bar_colors)

            from matplotlib.patches import Patch

            # 讀取 log 檔，累計子功能的耗時數值
            sub_time_summary = defaultdict(lambda: defaultdict(float))
            with open(log_path, "r", encoding='big5', errors='replace') as f:
                for line in f:
                    if "[Data Time]" in line:
                        match = re.search(r"\[Data Time\]\s+(.*?)\s+:\s+([\d.]+)", line)
                        if match:
                            tag = match.group(1).strip()
                            s = float(match.group(2))
                            # 如果 tag 為純數字，歸到 "收集資料&修改資料"
                            if tag.isdigit():
                                main_tag = "收集資料&修改資料"
                            else:
                                main_tag = feature_mapping.get(tag, "其他")
                            sub_time_summary[main_tag][tag] += s

            # 計算每個大功能的總耗時，用以排序（依降冪排列）
            total_time = {big: sum(sub_time_summary[big].values()) for big in sub_time_summary}
            sorted_big = sorted(total_time.items(), key=lambda x: x[1], reverse=True)

            # 準備大功能列表，以及每個大功能內的各子功能耗時與對應顏色
            big_labels = []
            big_values = []       # 每一項為該大功能內，各子功能耗時的 list（堆疊數值）
            big_sublabels = []    # 每一項為該大功能內各小功能名稱
            big_bar_colors = []   # 每一項為該大功能內各小功能的顏色

            for big, t in sorted_big:
                big_labels.append(big)
                # 針對每個大功能，排序子功能（根據耗時降序排列）
                sorted_sub = sorted(sub_time_summary[big].items(), key=lambda x: x[1], reverse=True)
                sub_times = [x[1] for x in sorted_sub]
                sub_tags = [x[0] for x in sorted_sub]
                # 依照小功能名稱分配顏色，若沒有對應預設灰色
                sub_colors = [color_map.get(sub, "#9E9E9E") for sub in sub_tags]
                big_values.append(sub_times)
                big_sublabels.append(sub_tags)
                big_bar_colors.append(sub_colors)

            # 畫出堆疊式水平長條圖
            fig, ax = plt.subplots(figsize=(10, len(big_labels) * 0.8))
            for i, (sub_times, sub_colors, sub_tags) in enumerate(zip(big_values, big_bar_colors, big_sublabels)):
                left = 0
                for time_val, sub_color, sub_tag in zip(sub_times, sub_colors, sub_tags):
                    # 畫出該段堆疊 bar
                    ax.barh(i, time_val, left=left, color=sub_color, edgecolor="white")
                    # 在 bar 中間顯示此子功能的耗時（例如 0.25s）
                    ax.text(left + time_val/2, i, f"{time_val:.2f}s", ha="center", va="center", fontsize=8, color="white")
                    left += time_val

            # 設定 y 軸與標題
            ax.set_yticks(range(len(big_labels)))
            ax.set_yticklabels(big_labels)
            ax.set_xlabel("Time (s)")
            ax.set_title("各大功能內各子功能耗時堆疊圖")
            ax.grid(True, axis="x")

            # 產生 legend（列出所有子功能對應的顏色）
            unique_subfeatures = set()
            for sub_list in big_sublabels:
                unique_subfeatures.update(sub_list)
            legend_handles = [Patch(color=color_map.get(sub, "#9E9E9E"), label=sub) for sub in unique_subfeatures]
            ax.legend(handles=legend_handles, title="子功能", loc='lower right')

            plt.tight_layout()
            plt.savefig(save_path)
            self.print_level_handle("info", f"✅ 已產生堆疊式時序圖 {save_path}")

        else:
            print("!!! 未啟動 Function_duration !!!")
            return
"""

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
        






# === Helper function for快速結束並記錄 === (結合log時間、大小紀錄 + 時間stop節點) 
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
    return elapsed




