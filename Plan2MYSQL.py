#將plan.csv中的資料輸入到資料庫裡，供php使用

import pymysql
import csv
def plan2mysql(file):
    connection = pymysql.connect(host='127.0.0.1',
                            port=3306,
                            user='root',
                            password='nclab722',
                            database='penghu',
                            charset='utf8')

    cursor = connection.cursor()

    sql1 = "DROP TABLE `plan` ;"
    cursor.execute(sql1)

    sql2 = '''
    CREATE TABLE `plan`(
        `no` VARCHAR(50),
        `Time` VARCHAR(50),
        `POI` VARCHAR(50),
        `UserID` VARCHAR(200),
        `設置點` VARCHAR(50),
        `緯度` VARCHAR(50),
        `經度` VARCHAR(50),
        `BPLUID` VARCHAR(50),
        `age` VARCHAR(50),
        `gender` VARCHAR(50),
        `天氣` VARCHAR(50)
        );
    '''
    cursor.execute(sql2)

    with open(file, mode='r', newline='' , encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        
        next(reader)
        
        for row in reader:
            sql3 = "INSERT INTO `plan` (no,Time,POI,UserID,設置點,緯度,經度,BPLUID,age,gender,天氣) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"
            cursor.execute(sql3, row)

    # 提交事務
    connection.commit()

    cursor.close()
    connection.close()
    print("csv already save in MySQL")
    
    
# plan2mysql('C:/Users/wkao_/Desktop/NCLab/penghu project/penghu_csv_file/plan.csv')