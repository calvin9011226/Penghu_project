from xgboost import XGBClassifier
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

def XGboost_recommend1(arr,gender,age):    
    le = LabelEncoder()
    labelencoder = LabelEncoder()
    tree_deep = 100 #可理解成epoch
    learning_rate = 0.3
    
    Data = pd.read_csv('C:/Users/wkao_/Desktop/NCLab/penghu project/penghu_csv_file/penghu_orignal2.csv',encoding='utf-8-sig')
    df_data = pd.DataFrame(data= np.c_ [Data['weather'], Data['gender'], Data['age'], Data['設置點']],
                           columns= ['weather','gender','age','label'])
    
    df_data['weather'] = labelencoder.fit_transform(df_data['weather'])#轉換文字要做one-hot encode前要先做label encode

    X = df_data.drop(labels=['label'],axis=1).values # 移除label並取得剩下欄位資料

    onehotencoder = OneHotEncoder(categories = 'auto')
    X=onehotencoder.fit_transform(X).toarray()    
    #print(list(X.columns))
    #R = pd.DataFrame(X)
    #print(R)
    Y = df_data['label'].values    
    
    
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3, random_state=42)# stratify=Y  -> 依据标签y，按原数据y中各类比例，分配给train和test，使得train和test中各类数据的比例与原数据集一样
    Y_train = le.fit_transform(Y_train) #由於字串無法做訓練，所以進行Label encoding編碼

    arr_labelencode = labelencoder.transform(arr) #用同一個labelencoder能transform到一樣的編碼
    Value_arr = np.array([arr_labelencode[0],gender,age])
    #print(Value_arr)
    final=onehotencoder.transform([Value_arr]).toarray()#用同一個onehotencoder能transform到一樣的編碼
    xgboostModel = XGBClassifier(n_estimators=tree_deep, learning_rate= learning_rate)
    xgboostModel.fit(X_train, Y_train)
    #xgboostModel.save_model('PHtest.model')
    predicted = xgboostModel.predict(final)
    #print('訓練集Accuracy: %.2f%% ' % (xgboostModel.score(X_train,Y_train) * 100.0))
    #predicted = xgboostModel.predict([X_test])
    result = le.inverse_transform(predicted)
    #importance = xgboostModel.feature_importances_
    #print(importance)
    #print(result[0])
    
    return predicted,result

def XGboost_recommend2(arr,gender,age,tidal,temperature):    
    le = LabelEncoder()
    labelencoder = LabelEncoder()
    tree_deep = 100 #可理解成epoch
    learning_rate = 0.3
    
    Data = pd.read_csv('C:/Users/wkao_/Desktop/NCLab/penghu project/penghu_csv_file/penghu_orignal2_sustainable.csv',encoding='utf-8-sig')
    df_data = pd.DataFrame(data= np.c_ [Data['weather'], Data['gender'], Data['age'] ,Data['tidal'],Data['temperature'],Data['設置點']],
                           columns= ['weather','gender','age','tidal','temperature','label'])
    #轉換文字要做one-hot encode前要先做label encode
    df_data['weather'] = labelencoder.fit_transform(df_data['weather'])
    # 移除label並取得剩下欄位資料
    X = df_data.drop(labels=['label'],axis=1).values 

    onehotencoder = OneHotEncoder(categories = 'auto',handle_unknown='ignore')
    X=onehotencoder.fit_transform(X).toarray()    
    #print(list(X.columns))
    #R = pd.DataFrame(X)
    #print(R)
    Y = df_data['label'].values    
    
    # stratify=Y  -> 依据标签y，按原数据y中各类比例，分配给train和test，使得train和test中各类数据的比例与原数据集一样
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3, random_state=42)
    #由於字串無法做訓練，所以進行Label encoding編碼
    Y_train = le.fit_transform(Y_train) 
    #用同一個labelencoder能transform到一樣的編碼
    arr_labelencode = labelencoder.transform(arr) 
    Value_arr = np.array([arr_labelencode[0],gender,age,tidal,temperature])
    #print(Value_arr)
    #用同一個onehotencoder能transform到一樣的編碼
    final=onehotencoder.transform([Value_arr]).toarray()
    
    xgboostModel = XGBClassifier(n_estimators=tree_deep, learning_rate= learning_rate)
    xgboostModel.fit(X_train, Y_train)
    xgboostModel.save_model('PHtest.bin')
    predicted = xgboostModel.predict([final[0]])
    print('訓練集Accuracy: %.2f%% ' % (xgboostModel.score(X_train,Y_train) * 100.0))
    #predicted = xgboostModel.predict([X_test])
    result = le.inverse_transform(predicted)
    #importance = xgboostModel.feature_importances_
    #print(importance)
    #print(result[0])
    
    return result[0]

def XGboost_plan(plan_data,gender,age):
    le = LabelEncoder()
    tree_deep = 100 #可理解成epoch
    learning_rate = 0.3
    
    Data = plan_data
    df_data = pd.DataFrame(data= np.c_ [Data['gender'], Data['age'], Data['UserID/MemID']],
                           columns= ['gender','age','label'])
    #轉換文字要做one-hot encode前要先做label encode
    
    X_train = df_data.drop(labels=['label'],axis=1).values # 移除label並取得剩下欄位資料    
    Y_train = df_data['label'].values    
    #print(X_train[0])
    #print(Y_train[0])
    
    
    #X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3, random_state=42)# stratify=Y  -> 依据标签y，按原数据y中各类比例，分配给train和test，使得train和test中各类数据的比例与原数据集一样
    Y_train = le.fit_transform(Y_train) #由於字串無法做訓練，所以進行Label encoding編碼
    #print('encode class:' +str( le.classes_.shape))
    #print(X_train[0])
    
    
    xgboostModel = XGBClassifier(n_estimators=tree_deep, learning_rate= learning_rate)
    xgboostModel.fit(X_train, Y_train)
    #xgboostModel.save_model('PHtest.model')
    test = np.array([gender,age])
    predicted = xgboostModel.predict([test])
    #print('訓練集Accuracy: %.2f%% ' % (xgboostModel.score(X_train,Y_train) * 100.0))
    #predicted = xgboostModel.predict([X_test])
    #print('訓練集: ',xgboostModel.score(X_train,Y_train))
    #print('測試集: ',xgboostModel.score(X_test,Y_test))
    #print(predicted)
    result = le.inverse_transform(predicted)
    #print(type(result))
    #print(result[0])
    return result[0] #回傳關聯性最高的UUID

#plan_data = pd.read_csv('C:/Users/roy88/testproject/python/xgboost/plan_2day.csv',encoding='utf-8-sig')
#print(XGboost_plan(plan_data,0,25))

arr = np.array("風雨")
arr = np.atleast_1d(arr)
print(XGboost_recommend2(arr,1,25,2,24))
#print(XGboost_recommend1(arr,1,69))