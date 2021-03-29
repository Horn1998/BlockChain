import pymongo
import traceback
import json
admin = pymongo.MongoClient("mongodb://localhost:27017/")
db = admin['blockchain']
register_col = db['register']
transaction_col = db['transaction']
block_col = db['block']

#用户注册
def register(client):
    try:
        print('执行mongo用户注册函数')
        required_fields = ['phone', 'pvt_key', 'pub_key', 'address']
        # 检查属性是否齐全
        for field in required_fields:
            if not client.get(field):
                print('数据不全')
                return "Invalid register data", 404
        result = register_col.find_one({'phone': client['phone']})
        if result:
            print('用户已经注册账户')
            return 'Invalid register data', 404
        if 'business_id' in client.keys():
            client['type'] = 'miner'
            result = register_col.find_one({'business_id': client['business_id']})
            if result:
                print('企业已经注册账户')
                return 'Invalid register data', 404
        else:
            client['type'] = 'user'
        register_col.insert_one(client)
        return "success insert client", 200
    except Exception:
        traceback.print_exc()

#交易记录
def trade(tx):
    try:
        required_fields = ['source_address', 'target_address', 'cash', 'power']
        for field in required_fields:
            if not tx.get(field):
                return "Invalid transaction data", 404
        transaction_col.insert_one(tx)
    except Exception:
        traceback.print_exc()


#添加区块
def bc_write(block):
    try:
        required_fields = ['index', 'timestamp', 'previous_hash', 'nonce', 'merkleroot', 'difficulty', 'merkletree', 'transactions']
        # block = json.loads(block)
        for field in required_fields:
            if not block.get(field):
                print('区块属性值不全')
                return "Invalid block data", 404
        block_col.insert_one(block)
    except Exception:
        traceback.print_exc()


#读取区块
def bc_read():
    """
    用于恢复区块链

    :return: chain_dump list
    """
    try:
        chain_dump = []
        for item in block_col.find():
            item.pop('_id')
            chain_dump.append(item)
        return chain_dump
    except Exception:
        traceback.print_exc()

if __name__ == '__main__':
    bc_read()