import tushare as ts 
import sys
import io
import json
import datetime
from sklearn.svm import SVR
import pandas as pd
from pandas_datareader import data, wb
import numpy as np
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')
class getshares:
    @classmethod
    def getsharesinfo(self,data):
        List= {}
        shares_string = data.split(',')
        df = ts.get_realtime_quotes(shares_string)
        sudf  = df[['name','open','pre_close','price','date','time','code']] 
        print(sudf)
        for i in sudf.index:
            inf = info(sudf.ix[i,0],sudf.ix[i,1],sudf.ix[i,2],sudf.ix[i,3],sudf.ix[i,4],sudf.ix[i,5],sudf.ix[i,6])
            json_str = json.dumps(inf, default=change)
            List[str(i)] = json_str 
        return List
    @classmethod
    def get_data(self,time,code):
        #today=datetime.date.today()
        df = ts.get_h_data(code,start=time, end="2018-07-16")  
        df = df.iloc[::-1,:]     
        CSV_PATH = r"D:\\vscodeproject\\test\\program4\\stock.csv"
        df.to_csv(CSV_PATH,header=True, index=True) 
    @classmethod
    def export_data(self):
        pass
    @classmethod
    def manange_data(self): 
        CSV_PATH = r"D:\\vscodeproject\\test\\program4\stock.csv"
        spy = pd.read_csv(CSV_PATH)
        for i in range(1, 21, 1):
            spy.loc[:,'Close Minus ' + str(i)] = spy['close'].shift(i)
        spy20 = spy[[x for x in spy.columns if 'Close Minus' in x or x == 'close' ]].iloc[20:,]
        spy20 = spy20.iloc[:,::-1]
        spy20.to_csv("D:\\vscodeproject\\test\\program4\\final.csv",header=True, index=True)
    @classmethod
    def forecast(self): 
        CSV_PATH = r"D:\\vscodeproject\\test\\program4\\final.csv"
        spy20 = pd.read_csv(CSV_PATH)
        spy = pd.read_csv("D:\\vscodeproject\\test\\program4\\stock.csv")
        clf = SVR(kernel='linear')
        X_train = spy20[:-400]
        y_train = spy20['close'].shift(-1)[:-400]
        model = clf.fit(X_train, y_train)
        x = spy20[-1:]
        X_test = spy20[-700:-400]
        y_test = spy20['close'].shift(-1)[-700:-400]
        preds = model.predict(x)
        pred = model.predict(X_test)
        tf = pd.DataFrame(list(zip(y_test, pred)), columns=['Next Day Close', 'Predicted Next Close'], index=y_test.index)
        #为tf数据集新增列是当前日期收盘价
        cdc = spy[['close']].iloc[-700:-400]
        #为tf数据集新增列是下一日开盘价
        #shift(-1)代表下一日
        ndo = spy[['open']].iloc[-700:-400].shift(-1)
        #将tf和新增列cdc当前日期收盘价合并，保留索引
        tf1 = pd.merge(tf, cdc, left_index=True, right_index=True)
        #将tf1和新增列ndo下一日期开盘价合并，保留索引
        tf2 = pd.merge(tf1, ndo, left_index=True, right_index=True)
        #新数据集tf2，重置列名
        tf2.columns = ['Next Day Close', 'Predicted Next Close', 'Current Day Close', 'Next Day Open']
        #设置新列，列名Signal，值为买入信号，1买入
        tf2 = tf2.assign(Signal = tf2.apply(get_signal, axis=1))
        #设置新列，列名PnL，值为盈亏比率
        tf2 = tf2.assign(PnL = tf2.apply(get_ret, axis=1))
        tf2.to_csv("D:\\vscodeproject\\test\\program4\\daily.csv",header=True, index=True)
        return preds
    @classmethod
    def trade(self):
        List = {}
        CSV_PATH = r"D:\\vscodeproject\\test\\program4\\stock.csv"
        spy = pd.read_csv(CSV_PATH)
        # 交易策略1：每日交易策略，每日回报率=（当前的收盘价 - 上一交易日的收盘价）/上一交易日收盘价
        daily_rtn = ((spy['close'] - spy['close'].shift(1))/spy['close'].shift(1))*100
        # 隔夜交易策略：隔夜交易收益率 = （当天开盘价 - 上一天收盘价）/上一天收盘价
        on_rtn = ((spy['open'] - spy['close'].shift(1))/spy['close'].shift(1))*100
        # 日间交易：收益 = 当天收盘价 - 当天开盘价
        id_rtn = ((spy['close'] - spy['open'])/spy['open'])*100
        #长期持有策略：
        long_rtn = ((spy['close'].shift(-1) - spy['open'][1:])/spy['close'].shift(-1))*100
        #自定义策略：
        tf = pd.read_csv("D:\\vscodeproject\\test\\program4\\daily.csv")
        res5 = getshares.get_stats(tf['PnL'])
        res5.set_name("自定义交易策略")
        json_str5 = json.dumps(res5, default=match)
        res4 = getshares.get_stats(long_rtn)
        res = getshares.get_stats(daily_rtn)
        res.set_name("每日交易策略")
        json_str = json.dumps(res, default=match)
        res2 = getshares.get_stats(on_rtn)
        res2.set_name("隔夜交易策略")
        json_str2 = json.dumps(res2, default=match)
        res3 = getshares.get_stats(id_rtn)
        res3.set_name("日间交易策略")
        json_str3 = json.dumps(res3, default=match)
        res4.set_name("长期持有策略")
        json_str4 = json.dumps(res4,default=match)
        List['0'] = json_str
        List['1'] = json_str2
        List['2'] =  json_str3
        List['3'] = json_str4
        List['4']  = json_str5
        return List

        
    @classmethod
    #统计信息方法
    def get_stats(self,s,n=252):
        #删除NaN数据
        s = s.dropna()
        #盈利次数：获取每日收益率大于0的所有数据，并计算总数
        wins = len(s[s>0])
        #亏损次数：获取每日收益率小于0的所有数据，并计算总数
        losses = len(s[s<0])
        #盈亏平衡次数：获取每日收益率等于0的所有数据，并计算总数
        evens = str(len(s[s==0]))
        #盈利平均值，round四舍五入，3为小数位数
        mean_w = round(s[s>0].mean(), 3)
        #亏损平均值
        mean_l = round(s[s<0].mean(), 3)
        #盈利亏损比例
        win_r = round(wins/losses, 3)
        #平均收益
        mean_trd = round(s.mean(), 3)
        #标准差
        sd = round(np.std(s), 3)
        #最大亏损
        max_l = round(s.min(), 3)
        #最大盈利
        max_w = round(s.max(), 3)
        sharpe_r = round((s.mean()/np.std(s))*np.sqrt(n), 4)
        #交易次数
        cnt = len(s)
        t = tongji(cnt,wins,losses,evens,win_r,mean_w,mean_l,mean_trd,sd,max_l,max_w,sharpe_r)
        return t
#交易策略统计类
class tongji:
    def __init__(self,cnt,wins,losses,evens,win_r,mean_w,mean_l,mean_trd,sd,max_l,max_w,sharpe_r):
        self.cnt = cnt
        self.wins = wins
        self.losses = losses
        self.evens = evens
        self.win_r = win_r
        self.mean_w = mean_w
        self.mean_l = mean_l
        self.mean_trd = mean_trd
        self.sd = sd
        self.max_l = max_l
        self.max_w = max_w
        self.sharpe_r = sharpe_r
    def set_name (self,name):
        self.name = name
#股票信息类
class info:
    name = ''
    open =''
    pre_close = ''
    price = ''
    date= ''
    time = ''
    code = ''
    def __init__(self,name,open,pre_close,price,date,time,code):
        self.name = name
        self.open = open
        self.pre_close = pre_close
        self.price = price
        self.date = date
        self.time = time
        self.code = code
def change(obj):
    return {
        "name":obj.name,
        "open":obj.open,
        "pre_close":obj.pre_close,
        "price":obj.price,
        "date":obj.date,
        "time":obj.time,
        "code":obj.code
    }
def match(obj):
    return {
        "name":obj.name,
        "cnt":obj.cnt,
        "wins":obj.wins,
        "losses":obj.losses,
        "evens":obj.evens,
        "win_r":obj.win_r,
        "mean_w":obj.mean_w,
        "mean_l":obj.mean_l,
        "mean_trd":obj.mean_trd,
        "sd":obj.sd,
        "max_l":obj.max_l,
        "max_w":obj.max_w,
        "sharpe_r":obj.sharpe_r
    }


#买入信号点，反向指标预测
def get_signal(r):
    if r['Predicted Next Close'] > r['Next Day Open'] + 1:
        return 0
    else:
        return 1
#盈亏比率
def get_ret(r):
    if r['Signal'] == 1:
        return ((r['Next Day Close'] - r['Next Day Open'])/r['Next Day Open']) * 100
    else:
        return 0