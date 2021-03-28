from hashlib import sha256
import traceback
import datetime
import json
import time
#区块
class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, merkletree,  merkleroot,  nonce=0, difficulty = 3):
        #区块头
        self.index = index                  #区块链位置
        self.timestamp = timestamp          #时间戳
        self.previous_hash = previous_hash  #父个区块的哈希
        self.nonce = nonce                  #存储有关工作量证明算法的难度目标
        # self.merkleroot = merkletree[-1] if len(merkletree) > 0 else None  #merkle根
        self.merkleroot = merkleroot
        self.difficulty = difficulty        #难度值

        #区块体
        self.merkletree = merkletree        #merkle树
        self.transactions = transactions    #交易信息

    #利用区块属性获取哈希
    def compute_hash(self):
        try:
            #将区块头数据打包成(把merkle树也加入计算，实际过程中不用）
            block_string = json.dumps(self.__dict__, sort_keys=True)
            return sha256(block_string.encode()).hexdigest()
        except Exception:
            traceback.print_exc()

class Blockchain:
    difficulty = 3
    def __init__(self):
        self.unconfirmed_transactions = []      #未上链的交易
        self.chain = []                         #区块链
        # 工作量证明算法难度值
        # self.difficulty = difficulty

    #构建创世区块
    def create_genesis_block(self):
        genesis_block = Block(0, [], 0, "0", ['0000000000'], '0000000000')
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

     #获取最后一个区块
    @property  #设置类属性值
    def last_block(self):
        return self.chain[-1]


    #添加区块
    def add_block(self, block, proof):
        """
        添加非创世区块:
        * 查看proof是否合理
        * 前一个区块的哈希是否和当前区块的记录值相同
        """
        previous_hash = self.last_block.hash
        if previous_hash != block.previous_hash:
            print('上一区块哈希值不对应')
            return False

        if not Blockchain.is_valid_proof(block, proof):
            print('工作量证明验证失败')
            return False
        print('添加新区块成功')
        block.hash = proof
        self.chain.append(block)
        return True

    #工作量证明算法
    @staticmethod
    def proof_of_work(block):
        block.nonce = 0
        time.sleep(3)
        computed_hash = block.compute_hash()
        #区块起始位置由多少个0组成
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    #添加新交易
    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)


    #区块合法性证明
    @classmethod
    def is_valid_proof(cls, block, block_hash):
        """
        检查当前区块的合法性以及是否满足难度要求
        """
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    #检查链的合法性(新节点加入时用到）
    @classmethod
    def check_chain_validity(cls, chain):
        previous_hash = "0"

        for block in chain:
            block_hash = block.hash
            #移除区块hash属性并重新计算hash
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block_hash) or \
                    previous_hash != block.previous_hash:
                return False

            block.hash, previous_hash = block_hash, block_hash
        return True

    #矿工函数
    def mine(self):
        try:
            #没有要打包的交易
            if not self.unconfirmed_transactions:
                return False
            #交易量不足，拒绝打包
            if len(self.unconfirmed_transactions) < 1:
                print(datetime.datetime.now(), '交易量不足，无法打包')
                return False

            last_block = self.last_block
            merkle_tree, merkle_head, tx = self.build_merkletree()
            new_block = Block(index=last_block.index + 1,
                              merkleroot=merkle_head,
                              timestamp=time.time(),
                              previous_hash=last_block.hash,
                              difficulty=self.difficulty,

                              merkletree=merkle_tree,
                              transactions=tx)

            proof = self.proof_of_work(new_block)
            self.add_block(new_block, proof)
            #清空交易池
            self.unconfirmed_transactions = []
            return True
        except Exception as ex:
            traceback.print_exc()

    def build_merkletree(self):
        """
        构建merkle树
        :return: merkle树，merkle根节点，打包交易内容
        """
        if not self.unconfirmed_transactions:
            return '无法构建Merkle树'
        else:
            tx_length = len(self.unconfirmed_transactions)
            MerkleTree, count, tot = [], 0, 0
            for i in range(tx_length):
                tx_hash = sha256(json.dumps(self.unconfirmed_transactions[i]).encode()).hexdigest()
                MerkleTree.append(tx_hash)
                # 交易为偶数才可以构建merkle树
                if len(MerkleTree) % 2 == 1: MerkleTree.append(MerkleTree[-1])
                count = len(MerkleTree)
            while count > 1:
                left, right = MerkleTree[tot], MerkleTree[tot+1]
                # hashcode = sha256((json.dumps(left.content) + json.dumps(right.content)).encode()).hexdigest()
                hashcode = sha256(left.encode() + right.encode()).hexdigest()
                MerkleTree.append(hashcode)
                count, tot = count - 1, tot + 1
            MerkleHead = MerkleTree[-1]
            print('MerkleTree', MerkleTree)
            print('MerkleHead', MerkleHead)
            print('tx', self.unconfirmed_transactions)
            #返回Merkle树,包含MerkTree的交易
            return MerkleTree, MerkleHead, self.unconfirmed_transactions