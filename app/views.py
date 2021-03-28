from flask import render_template, redirect, request
from Mongo.MongoDB import register, trade
from Client import Client
from app import app
import datetime
import json
import traceback
import requests

# The node with which our application interacts, there can be multiple
# such nodes as well.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8001"


requests.adapters.DEFAULT_RETRIES = 5 # 增加重连次数
s = requests.session()
s.keep_alive = False # 关闭多余连接

posts = []



def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    try:
        get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
        response = requests.get(get_chain_address)
        if response.status_code == 200:
            content = []
            chain = json.loads(response.content)
            for block in chain["chain"]:
                for tx in block["transactions"]:
                    tx["index"] = block["index"]
                    tx["hash"] = block["previous_hash"]
                    content.append(tx)

            global posts
            posts = sorted(content, key=lambda k: k['timestamp'],
                           reverse=True)
    except Exception:
        traceback.print_exc()



#加载主页
@app.route('/')
def index():
    fetch_posts()
    return render_template('index.html',
                           title='去中心化网络 '
                                 '区块链查询',
                           posts=posts,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)


#发起交易
@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application.
    """
    try:
        post_content = request.form["content"]
        author = request.form["author"]

        post_object = {
            'author': author,
            'content': post_content,
        }

        # Submit a transaction
        new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

        requests.post(new_tx_address,
                      json=post_object,
                      headers={'Content-type': 'application/json'})

        return redirect('/')
    except Exception:
        traceback.print_exc()
        return redirect('/')

@app.route('/option')
def option():
    return render_template('option.html', title='交易申请')


#注册账户
@app.route('/register', methods=['POST'])
def registers():
    """
    client属性
    :param phone:电话号码
    :param pvt_key:私
    :param pub_key:公钥
    :param address: 地址
    :return:
    """
    c, client = Client(), {}
    client['pvt_key'], client['pub_key'], client['address'] =c.pvt_pkcs, c.pub_pkcs, c.get_address()
    client['phone'] = request.form['phone']
    register(client)
    return render_template('option.html',
                           title='用户操作')


#用户操作函数
@app.route('/trade', methods=['POST'])
def trade():
    try:
        print(request.form)
        option={}
        option['address'] = request.form['address']
        option['cash'] = float(request.form['cash'])
        option['power'] = float(request.form['power'])
        option['character'] = int(request.form['character'])
        # Submit a transaction
        new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

        requests.post(new_tx_address,
                      json=option,
                      headers={'Content-type': 'application/json'})
        return redirect('/option')
    except Exception:
        traceback.print_exc()
        return redirect('/option')



def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')