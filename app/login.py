from flask import render_template, redirect, request, Response
from Mongo.MongoDB import mongo_register, mongo_trade, user_read
from hashlib import sha256
from Client import Client
import traceback
from app import app
import requests
import json
import rsa

requests.adapters.DEFAULT_RETRIES = 5 # 增加重连次数
s = requests.session()
s.keep_alive = False # 关闭多余连接
#—————————————————————————登录——————————————————————————————
#登录
@app.route('/')
def login():
    return render_template('login.html', title='Login to your account')

#获取本地私钥
@app.route('/get_pvk', methods=['POST'])
def get_pvk():
    UserID = request.form['UserID']
    user_dump = user_read()
    pvk_dump = []
    for user in user_dump:
        #如果是普通用户
        if 'business_id' not in user.keys() and user['phone'] == UserID:
            pvk_dump.append(str(user['pvt_key']))
        elif 'business_id' in user.keys() and user['business_id'] == UserID:
            pvk_dump.append(str(user['pvt_key']))
    ans = {'ans': pvk_dump}
    return Response(json.dumps(ans))


#验证账号的合法性
@app.route('/verified', methods=['POST'])
def verified():
    try:
        PrivateKey = request.form['PrivateKey']
        UserID = request.form['UserID']
        user_dump = user_read()
        pvk_dump = None
        for user in user_dump:
            if str(user['pvt_key']) == PrivateKey: pvk_dump = user
            # # 如果是普通用户
            # if 'business_id' not in user.keys() and user['phone'] == UserID:
            #     pvk_dump.append(user)
            # elif 'business_id' in user.keys() and user['business_id'] == UserID:
            #     pvk_dump.append(user)
        if not pvk_dump: return render_template('login.html', title='登录失败')
        private_key = rsa.PrivateKey.load_pkcs1(pvk_dump['pvt_key'])
        # 签名
        result = rsa.sign(UserID.encode('utf-8'), private_key, 'SHA-256')
        if result == pvk_dump['sign']:
            print('登陆成功')
            return render_template('home.html', title='主页面')
        else:
            print('登陆失败')
            return render_template('login.html', title='登录失败')
    except Exception:
        traceback.print_exc()
        return render_template('login.html', title='登录失败')



#—————————————————————————注册—————————————————————————————
#注册
#能源认证
@app.route('/register')
def register():
    return render_template('register.html', title1='矿工注册', title2='用户注册')


#用户操作函数
@app.route('/miner_register', methods=['POST'])
def miner_register():
    try:
        print(request.form)
        c, miner=Client(), {}
        miner['business_id'] = request.form['id'] #该id是否有交易许可
        miner['position'] = float(request.form['position'])
        miner['power_type'] = request.form['power']
        miner['limit'] = int(request.form['limit'])
        miner['pvt_key'], miner['pub_key'], miner['address'] = c.pvt_pkcs, c.pub_pkcs, c.get_address()
        miner['phone'] = request.form['phone']
        private_key = rsa.PrivateKey.load_pkcs1(c.pvt_pkcs)
        miner['sign'] = rsa.sign(miner['business_id'].encode('utf-8'), private_key, 'SHA-256')
        mongo_register(miner)
        # Submit a transaction
        return render_template('login.html',
                               title1='矿工注册成功', title2='用户注册')
    except Exception:
        traceback.print_exc()
        return render_template('register.html',
                               title1='矿工注册失败', title2='用户注册')


#注册账户
@app.route('/user_register', methods=['POST'])
def user_register():
    """
    client属性
    :param phone:电话号码
    :param pvt_key:私
    :param pub_key:公钥
    :param address: 地址
    :return:
    """
    try:
        c, client = Client(), {}
        client['pvt_key'], client['pub_key'], client['address'] =c.pvt_pkcs, c.pub_pkcs, c.get_address()
        client['phone'] = request.form['phone']
        private_key = rsa.PrivateKey.load_pkcs1(c.pvt_pkcs)
        client['sign'] = rsa.sign(client['phone'].encode('utf-8'), private_key, 'SHA-256')
        mongo_register(client)
        return render_template('login.html',
                               title1='矿工注册', title2='用户注册成功')
    except Exception:
        traceback.print_exc()
        return render_template('register.html',
                               title1='矿工注册', title2='用户注册失败')

