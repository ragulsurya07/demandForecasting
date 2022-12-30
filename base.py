from flask import Flask,request,json
import numpy as np
import os 
import pandas as pd
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
from sklearn.linear_model import LinearRegression


api = Flask(__name__)

api.config['MYSQL_HOST'] = 'localhost'
api.config['MYSQL_USER'] = 'root'
api.config['MYSQL_PASSWORD'] = 'database password'
api.config['MYSQL_DB'] = 'database name'

mysql = MySQL(api)


#least square regression
@api.route('/l_regrsn', methods=['POST'])
def l_regression():
    try:
        reqdata_data = json.loads(request.data)
        month=int(reqdata_data['forecast'])
        mon=['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
        X = [1,2,3,4,5,6,7,8,9,10,11,12]
        Y = []
        for i in range(len(reqdata_data['content'])):
            Y.append(int(reqdata_data['content'][mon[i]]))
        mean_x = np.mean(X)
        mean_y = np.mean(Y)
        n = len(X)
        numer = 0
        denom = 0
        for i in range(n):
            numer += (X[i] - mean_x) * (Y[i] - mean_y)
            denom += (X[i] - mean_x) ** 2
            m = numer / denom
            c = mean_y - (m * mean_x)
        f=(month*m)+c
        x = np.linspace(1, 12, 10)
        y = c + m * x
        f = round(f)
        y = list(y)
        return {'forecast':f, 'yvalues': y, 'sales': Y}
    except:
        print("========> An exception occurred - ValueError <========")
        return {'error1' : "Enter a valid input"}

#linear regression
@api.route('/linear_regrsin', methods=['POST'])
def datafrmfrntend():
    req_data = json.loads(request.data)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    vehicle=req_data['content'] 
    frontErr = func(vehicle)  # handleError of user wrong inputs
    print(frontErr)
    def yearcalculation():
        dates=[]
        endpoint = date.today() + relativedelta(months=-14)
        for mon in range(12):
            endpoint=endpoint + relativedelta(months=+1)
            dates.append(str(endpoint.month)+"/"+str(endpoint.year))
        # print(dates)
        return(dates)
    
    def datafetching():
        msales=[]
        Tmonths=yearcalculation()
        for month in range (len(Tmonths)):
            date="%"+Tmonths[month]+"%"
            datas=[date,vehicle]
            sql='select * from finaldata where date LIKE %s and model=%s'
            cursor.execute(sql,datas)
            sales=cursor.fetchall()
            sales=list(sales)
            Tsales=0
            for sale in range(len(sales)):
                Tsales=Tsales+sales[sale]['count']
            msales.append(Tsales)
        return(msales)
    
    def l_regression():
        x = np.array([1,2,3,4,5,6,7,8,9,10,11,12]).reshape((-1, 1))
        y = np.array(datafetching())
        model = LinearRegression().fit(x, y)
        y_pred = model.predict(x)
        return(y_pred)
    result=list(l_regression())
    asales=datafetching()
    cursor.close()
    return {'result':result, 'sales':asales, 'Err': frontErr}


def func(vehicle):
    try:
        for itms in my_profile()['model']:
            if itms == vehicle:
                match = 'Equal'
                return match
        else:
            notMatch = 'Not equal'
            return notMatch
    except:
        print('=====> Error occured! <=====')
        return {'error2' : "Please check the correct spelling!"}
    


#fetching bike models
@api.route('/model')
def my_profile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = 'select model from modelname'
    cursor.execute(sql)
    rslt = list(cursor.fetchall())
    model = []
    for i in range(len(rslt)):
        model.append(rslt[i]['model'])
    return {'model':model}


#file upload
@api.route('/upload', methods = ['GET', 'POST'])
def uploader_file():
    try:
        f = request.files['file']
        filesname=f.filename
        f.save(os.path.join("/home/akitra/Training_files/Demand Forecasting 3/UploadFiles",f.filename))
        car=pd.read_csv("/home/akitra/Training_files/Demand Forecasting 3/UploadFiles/"+filesname)
        df = pd.DataFrame(car)
        y = np.array(df['sale'])
        # def l_regression():
        x = np.array([1,2,3,4,5,6,7,8,9,10,11,12]).reshape((-1, 1))
        model = LinearRegression().fit(x, y)
        y_pred = model.predict(x)
        prediction = list(y_pred)
        yvalues = list(df['sale'])
        # prediction=list(l_regression())
        return { 'data':prediction, 'yvalues': yvalues }
    except:
        return 'Enter the correct format'


#spareParts 
@api.route('/spare',methods=['POST'])
def spare():
    try:
        spare_data=json.loads(request.data)
        vehicle = []
        vehicle.append(spare_data['data'])
        spare = spare_data['spare']
        month = spare_data['month']
        year = str(date.today().year)
        year = month+"-01-"+year
        date_object = datetime.strptime(year, '%m-%d-%Y').date()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        def expiry():
            sql='select id from sparemodels where model = %s'
            cursor.execute(sql,vehicle)
            rslt=cursor.fetchall()
            tbname = rslt[0]['id']
            sql='select expire from '+tbname+' where spare = %s'
            data = [spare]
            cursor.execute(sql,data)
            rslt = cursor.fetchall()
            exp = rslt[0]['expire']
            return(exp)
        def calculation():
            expry = int(expiry())
            endpoint = date_object + relativedelta(months=-expry)
            mnth=str(endpoint)
            dates='%'+mnth[5:7]+'/'+mnth[:4]+'%'
            vehicle.append(dates)
            vehicle[0],vehicle[1]=vehicle[1],vehicle[0]
            sql='select * from finaldata where date LIKE %s and model=%s'
            cursor.execute(sql,vehicle)
            sales=cursor.fetchall()
            sales=list(sales)   
            Tsales=0
            for sale in range(len(sales)):
                Tsales=Tsales+sales[sale]['count']
            return(Tsales)
        predict=calculation()
        print(predict)
        return{'forecast':predict}
    except:
        print("========> An exception occurred - ValueError <========")
        return {'error' : "Enter a valid input"}

@api.route('/models')
def sparedmodel():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql='select model from sparemodels'
        cursor.execute(sql)
        sparemodel=list(cursor.fetchall())
        model = []
        for i in range(len(sparemodel)):
            print(i)
            model.append(sparemodel[i]['model'])
        return{'s':model}

@api.route('/sparepart',methods=['POST'])
def spareparts():
    spare_data=json.loads(request.data)
    vehicle = []
    vehicle.append(spare_data['data'])
    print(type(spare_data['data']))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql='select id from sparemodels where model=%s'
    cursor.execute(sql,vehicle)
    sparemodel=list(cursor.fetchall())
    id=[]
    id.append(sparemodel[0]['id'])
    ids=str(id[0])
    print(ids)
    sql='select spare from '+ids
    cursor.execute(sql)
    part=list(cursor.fetchall())
    print(part)
    model = []
    for i in range(len(part)):
        model.append(part[i]['spare'])
    print(model)
    return{'s':model}



if(__name__) == '__main__':
    api.run(debug=True )
