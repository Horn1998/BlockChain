from API.Genetic import run
import numpy as np
import copy
def trade(beta = 0.25, provider = None, demander = None):
    #下方为仿真数据
    block_index = 1
    #从区块中读取的交易数据
    provider = {'A': [1000, -400],  'B': [1500, -400], 'C': [2000, -300], 'D': [2000, -200]}
    demander = {'甲': [1500, -10], '乙': [1500, -20], '丙': [1000, -50], '丁': [3000, -100]}
    #用户输入的范围数据,交易地址
    POWER_BOUND, PRICE_BOUND = [500, 1700], [-400, -100]
    address = 'B'

    spread = {}
    temp_p, temp_d = copy.deepcopy(provider), copy.deepcopy(demander)
    #计算价差对
    for seller in provider.keys():
        for buyer in demander.keys():
            parties = (seller, buyer)
            spread[parties] = provider[seller][1] - demander[buyer][1]

    #按值对价差对进行排序
    sorted_spread = sorted(spread.items(), key=lambda kv: (kv[1], kv[0]))

    #集中撮合
    #当前拥有同等交易资格的角色可以根据信用度进行交易排序
    profit, tx = 0, {} #记录收益与完成交易
    for spread in sorted_spread:                            #遍历每一组交易
        provide, demand = provider[spread[0][0]], demander[spread[0][1]]
        if provide[0] == 0 or demand[0] == 0: continue
        if provide[0] >= demand[0]:                         #卖方电力充足，可以售卖
            tx[(spread[0][0], spread[0][1])] = demand[0]    #实际交易电量
            profit += (provide[1] - demand[1]) * demand[0]  #差价收益
            provider[spread[0][0]][0] -= demand[0]          #确认出售,电量减少
            demander[spread[0][1]][0] = 0                   #购电任务完成
        elif provide[0] < demand[0]:                        #卖方电力不足，买方仍然需要继续购电
            tx[(spread[0][0], spread[0][1])] = provide[0]   #实际交易电量
            profit += (provide[1] - demand[1]) * provide[0] #差价收益
            demander[spread[0][1]][0] -= provide[0]         #确认出售,电量减少
            provider[spread[0][0]][0] = 0                   #售电任务完成
    # print(tx, profit)
    #总返还价差
    r_provider, r_demander = profit * (1 - beta), profit * beta
    #各角色返还价差
    total_provider, total_demander, r_p_l, r_d_l = 0, 0, [], []
    for key in demander.keys(): total_demander += demander[key][1] * (temp_d[key][0] - demander[key][0])  #需求方价差之和
    for key in provider.keys(): total_provider += provider[key][1] * (temp_p[key][0] - provider[key][0])  #供给方价差之和
    # 公式：
    # 供给方返还价差总和： ΣEp= profit * (1 - beta)
    # 申请电量价差总和: ΣEd = Σprice * power
    # 单参与方返还价差：Ep = ΣEp *  Ed/ ΣEd
    # 价差波动： price = Ep/power = ΣEp * price / ΣEd
    for key in demander.keys(): r_d_l.append(r_demander * demander[key][1] / total_demander)
    for key in provider.keys(): r_p_l.append(r_provider * provider[key][1] / total_provider)
    # print(r_d_l, r_p_l,  profit * beta, profit * (1 - beta))
    for index, key in enumerate(provider.keys()): provider[key][1] -= r_p_l[index]
    for index, key in enumerate(demander.keys()): demander[key][1] += r_d_l[index]
    # for p_key in provider.keys(): print(p_key, '交易方报价', provider[p_key][1])
    # for d_key in demander.keys(): print(d_key, '需求方报价', demander[d_key][1])
    #生成账单（交易双方，交易电量，交易价格）
    billing = []
    for key in tx.keys():
        deal = {}
        deal['provider'] = key[0]
        deal['demander'] = key[1]
        deal['power'] = tx[key]
        deal['cash'] = tx[key] * abs(provider[key[0]][1] - demander[key[1]][1])
        billing.append(deal)
    # print(billing)
    #计算节约成本与提升收益
    for d_key in demander.keys():
        profit = (temp_d[d_key][1] - demander[d_key][1]) * (temp_d[d_key][0] - demander[d_key][0])  #需求方价差之和
        print(d_key, '节约支出', profit)
    for p_key in provider.keys():
        profit = (provider[p_key][1] - temp_p[p_key][1]) * (temp_p[p_key][0] - provider[p_key][0])  #供给方价差之和
        print(p_key, '增加收益', profit)
    # power, price, profit = run(POWER_BOUND, PRICE_BOUND)
    # original = (provider[address][1] - temp_p[address][1]) * (temp_p[address][0] - provider[address][0])
    # print('原始收益', original)
    # print('最佳收益', profit, '发电量', power, '价格', price)
    # print('额外增收', round(profit - original, 2))
    # ['买方', '电量', '价差', '收益']
    p_answer, d_answer = [], []
    for key in provider.keys():
        temp = []
        temp.append(key)                                    #角色
        temp.append(round(temp_p[key][0] - provider[key][0], 2))      #电量
        temp.append(round(provider[key][1],2))                   #价差
        profit = (provider[key][1] - temp_p[key][1]) * (temp_p[key][0] - provider[key][0])  #供给方价差之和
        temp.append(round(profit,2))                                 #额外收益
        p_answer.append(temp)
    for key in demander.keys():
        temp = []
        temp.append(key)                                    #角色
        temp.append(round(temp_d[key][0] - demander[key][0], 2))      #电量
        temp.append(round(demander[key][1], 2))                   #价差
        profit = (temp_d[key][1] - demander[key][1]) * (temp_d[key][0] - demander[key][0])  #需求方价差之和
        temp.append(round(profit, 2))                                 #额外收益
        d_answer.append(temp)
    return p_answer, d_answer






if __name__ == '__main__':
    p_answer, _ =trade()
    print(p_answer)
