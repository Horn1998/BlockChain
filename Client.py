# -*- coding:utf-8 -*-
from flask import Flask, request
from hashlib import sha256, new
import requests
import traceback
import chardet
import rsa
import json
import time



# app = Flask(__name__)

CLIENT_URL = 'http://127.0.0.1:8000'
MINER_URL = 'http://127.0.0.2:8001'
clients = []    #用户集合


class Client:
    def __init__(self):
        (pubkey, prvkey) = rsa.newkeys(1024)
        self.pub_pkcs = pubkey.save_pkcs1()
        self.pvt_pkcs = prvkey.save_pkcs1()
        self.public_key = rsa.PublicKey.load_pkcs1(self.pub_pkcs)
        self.private_key = rsa.PrivateKey.load_pkcs1(self.pvt_pkcs)
        self._address = self.get_address()  #正规获得address方式


    #私钥解密
    def private_decrypt(self, encrypt_info):
        return rsa.decrypt(encrypt_info, self.private_key)


    #公钥加密
    def public_encrypt(self, message):
        return rsa.encrypt(message.encode('utf-8'), self.public_key)


    #签名
    def sign(self, message):
        result = rsa.sign(message.encode('utf-8'), self.private_key, 'SHA-256')
        return result


    #验证签名（有问题）
    def verify_sign(self, message, encrypt_info, public_key):
        """
        :param message: 原信息
        :param encrypt_info: 私钥加密信息
        :param public_key: 发起者公钥
        :return:
        """
        try:
            ans = rsa.verify(message.encode('utf-8'), encrypt_info, public_key)
            return True
        except Exception:
            traceback.print_exc()
            return False


    #获得公钥地址
    def get_address(self):
        pub_key = ''
        for partial_key in str(self.pub_pkcs).split('\\n')[1:-1]:
            pub_key += partial_key
        one_step = sha256(pub_key.encode('utf-8')).hexdigest() #SHA-256
        two_step = new('ripemd160', one_step.encode('utf-8'))
        return two_step.hexdigest()



#展示所有用户
# @app.route('/show_client', methods=['GET'])
def show_client():
    ans = []
    for item in clients:
        ans.append(['address', item._address,'back', item.backup])
    return json.dumps({'ans':ans})


# @app.route('/retrieve', methods=['GET'])
def retrieve():
    data = request.get_json()
    #确定当前检查交易池的矿工
    miner_url = data['url']
    for client in clients:
        finished = []  #记录已经进入区块交易索引
        for index, tx in enumerate(client.backup):
            post_data = {
                'hash': tx['hash']
            }
            new_tx_address = "{}/miner_retrieve".format(miner_url)
            #查看当前交易是否进入区块链
            answer = requests.post(new_tx_address,
                                   json=post_data,
                                   headers={'Content-type':'application/json'})
            if str(answer.content.decode()) == 'fail':
                continue
            else: finished.append(index)
        #删除已经打包进入区块链的交易
        for index in reversed(finished):
            client.backup.pop(index)

clients.append(Client())
clients.append(Client())


if __name__ == '__main__':
    c = Client()
    print(type(c.private_key))
    print(c.pvt_pkcs)
    print(chardet.detect(c.pvt_pkcs))
