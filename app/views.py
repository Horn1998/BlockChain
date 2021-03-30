from flask import render_template, redirect, request
from API.Concentrated import trade as transaction
from app import app
import datetime
import traceback
import requests
import json

# The node with which our application interacts, there can be multiple
# such nodes as well.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"
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
@app.route('/option0')
def option0():
    fetch_posts()
    print(request.host_url, CONNECTED_NODE_ADDRESS)
    return render_template('block.html',
                           title='去中心化网络 '
                                 '区块链查询',
                           posts=posts,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)


#发起交易
@app.route('/search', methods=['POST'])
def search_block():
    """
    Endpoint to create a new transaction via our application.
    """
    try:
        # post_content = request.form["content"]
        bID = request.form["blockID"]
        fetch_posts()
        new_posts = []
        for item in posts:
            if item['index'] == int(bID):
                new_posts.append(item)
        return render_template('block.html',
                               title='去中心化网络 '
                                     '区块链查询',
                               posts=new_posts,
                               node_address=CONNECTED_NODE_ADDRESS,
                               readable_time=timestamp_to_string)


        return redirect('/option0')
    except Exception:
        traceback.print_exc()
        return redirect('/option0')


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')


#———————————————————————————————————————————————————#
#交易申请
@app.route('/option1')
def option1():
    return render_template('option.html', title='交易申请')


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
        return redirect('/option1')
    except Exception:
        traceback.print_exc()
        return redirect('/option1')


#————————————————————————————————————————————————————#
@app.route('/option3')
def option3():
    labels = ['参与方', '电量', '价差', '收益']
    p_answer, q_answer = transaction()
    print(p_answer)
    return render_template('result.html', labels=labels, p=p_answer, q=q_answer, title='结果查询')