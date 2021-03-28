from hashlib import sha256
from Block.Core import Block, Blockchain
from Mongo.MongoDB import bc_write, bc_read
from flask import Flask, request
from Client import Client
import requests
import traceback
import datetime
import json
import time

app = Flask(__name__)

#公共区块链(电力市场）
blockchain = Blockchain()
#创建创世区块（电力市场）
blockchain.create_genesis_block()

# 网络中矿工集合
peers = set()
#轻节点所在网络
CLIENT_URL = 'http://127.0.0.1:8000'


#添加新交易
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    try:
        tx_data = request.get_json()
        required_fields = ["address", "power", "cash"]
        print('开始提交新交易')
        # 检查属性是否齐全
        for field in required_fields:
            if not tx_data.get(field):
                print('数据不全')
                return "Invalid transaction data", 404
        # post_object = {
        #     "target_name": tx_data["target_name"]
        # }
        # new_tx_address = "{}/get_sign".format(CLIENT_URL)
        # answer = requests.post(new_tx_address,
        #                        json=post_object,
        #                        headers={'Content-type': 'application/json'})
        #
        # sign = json.loads(answer.content.decode())
        # new_tx_address = "{}/verify_sign".format(CLIENT_URL)
        # post_object = {
        #     "target_name": tx_data["target_name"],
        #     "source_name": tx_data["source_name"],
        #     "public_key": sign["public_key"],
        #     "content": sign["sign"],
        #     "cash": float(tx_data["cash"])
        # }
        # answer = requests.post(new_tx_address,
        #               json=post_object,
        #               headers={'Content-type': 'application/json'})
        #
        # print(str(answer.content.decode()))
        # timestamp = str(answer.content.decode())
        # if str(answer.content.decode()) == 'fail':
        #     return "error address", 404
        tx_data["timestamp"] = int(datetime.datetime.now().timestamp() * 10000)
        tx_data['hash'] = sha256(json.dumps(tx_data).encode('utf-8')).hexdigest()
        blockchain.add_new_transaction(tx_data)
        return "Success", 201
    except Exception:
        traceback.print_exc()
        return 'fail'



# 返回区块链的副本
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        #__dict__避免逐个添加属性键值对
        bc = block.__dict__
        bc.setdefault('_id', 0)
        bc.pop('_id')
        chain_data.append(bc)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data,
                       "peers": list(peers)})


#挖矿函数
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "mine fail"
    else:
        #保存当前区块链长度
        chain_length = len(blockchain.chain)
        consensus()
        #保证区块加入到最长区块链中
        if chain_length == len(blockchain.chain):
            #声明区块链最后一个区块已经挖出,且是当前矿工获得
            announce_new_block(blockchain.last_block)
            print(datetime.datetime.now(), '区块被挖出')
            #从交易池中删除上链交易
            pass
            #区块记录如数据库保存
            bc_write(blockchain.last_block.__dict__)
        else:
            #将节点区块链更新成最长区块链
            print('当前链不是最长链，将区块链更新为最长链')
            #当前区块挖去失败
            return '挖矿失败'
        return "Block #{} is mined.".format(blockchain.last_block.index)


# 添加新矿工入网并将最长链副本返回
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    #生成公私钥的区块链可以将自己的地址广播到区块中，这里以URL代替（不合理）
    #node_address:127.0.0.1：port
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    print(request.host_url, node_address)
    # 将新矿工加入矿工集合
    peers.add(node_address)

    #将最长链副本交给当前矿工
    return get_chain()


#向老矿工请求区块链副本
@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # update chain and the peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        #合并两个集合，重复元素只会出现一次
        peers.update(response.json()['peers'])
        announce_new_peer(data)
        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code


#新矿工下载并保存区块链副本
def create_chain_from_dump(chain_dump):
    generated_blockchain = Blockchain()
    generated_blockchain.create_genesis_block()
    for idx, block_data in enumerate(chain_dump):
        if block_data['index'] == 0:
            continue  # skip genesis block
        block = Block(index = block_data["index"],
                      transactions=block_data["transactions"],
                      timestamp=block_data["timestamp"],
                      previous_hash=block_data["previous_hash"],
                      merkletree=block_data["merkletree"],
                      merkleroot=block_data["merkleroot"],
                      nonce=block_data["nonce"],
                      difficulty=block_data["difficulty"])
        proof = block_data['hash']
        #不同节点区块链分离
        added = generated_blockchain.add_block(block, proof)
        if not added:
            raise Exception("The chain dump is tampered!!")
    return generated_blockchain


#矿工节点添加合法区块
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block(index = block_data["index"],
                  transactions=block_data["transactions"],
                  timestamp=block_data["timestamp"],
                  # timestamp=int(datetime.datetime.now().timestamp() * 10000),
                  previous_hash=block_data["previous_hash"],
                  merkleroot=block_data['merkleroot'],
                  merkletree=block_data["merkletree"],
                  nonce=block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201


#查看当前交易池中未确认交易
@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


@app.route('/run')
def run():
    while True:
        result = blockchain.mine()
        #挖矿失败，挖矿耗时3s
        if not result:
            time.sleep(3)
        else:
            chain_length = len(blockchain.chain)
            consensus()
            print(time.time(), '区块被挖出')
            if chain_length == len(blockchain.chain):
                answer = announce_new_block(blockchain.last_block)
                if answer == False: print('当前挖出区块不符合要求')

    return request.host_url + '挖矿成功'


#保证交易不会丢失，并且删除上链交易
@app.route('/miner_retrieve', methods=['POST'])
def miner_retrieve():
    tx_data = request.get_json()
    tx_hash = tx_data['hash']
    for block in blockchain.chain:
        for tx in block['merkletree']:
            #交易已经进入区块
            if tx_hash == tx['hash']:
                #从交易池中删除相应交易
                blockchain.unconfirmed_transactions.remove(tx)
                return 'success', 200
    #当前交易尚未打包上链
    return 'fail', 500


#将最长链作为主链
def consensus():
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get('{}chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False


#广播待加入区块，进行审核
def announce_new_block(block):
    #向其它矿工广播新加入节点
    for peer in peers:
        url = "{}add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        response = requests.post(url,
                      data=json.dumps(block.__dict__, sort_keys=True),
                      headers=headers)
        print(peer, '清理交易池')


#广播新加入矿工
def announce_new_peer(miner):
    for peer in peers:
        url = "{}register_node".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(miner),
                      headers=headers)

#启动区块链恢复节点
@app.route('/restart')
def restart():
    try:
        #获取历史区块链数据
        chain_dump = bc_read()
        global blockchain
        global peers
        blockchain = create_chain_from_dump(chain_dump)
        for peer in peers:
            node_address = request.host_url[:-1]
            data = {"node_address": node_address}
            headers = {'Content-Type': "application/json"}
            requests.post(peer + "register_with", data=json.dumps(data), headers=headers)
        return 'success', 200
    except Exception:
        traceback.print_exc()
        return 'success', 200
