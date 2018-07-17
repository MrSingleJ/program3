from flask import Flask,jsonify
from flask import Flask,url_for,redirect,render_template,request
from Auth.get_shares_info import *
app = Flask(__name__)
@app.route('/test',methods=["POST"])
def hello_world():
    test = request.form.get('share')
    sharesinfo = getshares.getsharesinfo(test)  
    return jsonify(sharesinfo)
@app.route('/stock', methods=["POST"])
def get_stock_front(): 
    id = request.form.get('stock')
    return  render_template("second.html",content = id)
@app.route('/export',methods=["GET"])
def export_data(): 
    return  ("导出数据成功！")
@app.route('/collect',methods=["POST"])
def collect_data():
    time = request.form.get('time')
    code = request.form.get('code')
    getshares.get_data(time,code)
    return  ("采集数据成功！")
@app.route('/manage',methods=["GET"])
def manage_data():
    getshares.manange_data()
    return  ("加工数据成功!")
@app.route('/forecast',methods=["GET"])
def forecast_data():
    res = getshares.forecast()
    res1 = str(res)
    return  ("预测明天的收盘价"+res1)
@app.route('/trade',methods=["POST"])
def trade_str():
    res = getshares.trade()
    return  jsonify(res)
@app.route('/')
def hello():
    return render_template("first.html", content="hello flask ")
if __name__ == '__main__':
    app.run(debug=True)


