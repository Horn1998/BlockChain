import numpy as np
import copy
def trade(beta = 0.25, provider = None, demander = None):
    #下方为仿真数据
    block_index = 1
    provider = {'A': [1000, -400],  'B': [1500, -400], 'C': [2000, -300], 'D': [2000, -200]}
    demander = {'甲': [1500, -10], '乙': [1500, -20], '丙': [1000, -50], '丁': [3000, -100]}


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
        profit = ( provider[p_key][1] - temp_p[p_key][1]) * (temp_p[p_key][0] - provider[p_key][0])  #供给方价差之和
        print(p_key, '增加收益', profit)


def adjust(beta=0.75, power=0, price=0):
    #下方为仿真数据
    block_index = 1
    provider = {'A': [500, -400],  'B': [power, price], 'C': [2000, -300], 'D': [2000, -200], 'A1': [1000, -350],  'B1': [1000, -250], 'C1': [2000, -300], 'D1': [2000, -200]}
    demander = {'甲': [1500, -10], '乙': [1500, -20], '丙': [1000, -50], '丁': [3000, -100], '甲1': [1500, -10], '乙1': [1500, -20], '丙1': [1000, -50], '丁1': [3000, -100]}


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
    total_provider, total_demander, r_p_d, r_d_d = 0, 0, {}, {}
    for key in demander.keys():
        total_demander += demander[key][1] * (temp_d[key][0] - demander[key][0])  #需求方价差之和
    for key in provider.keys():
        total_provider += provider[key][1] * (temp_p[key][0] - provider[key][0])  #供给方价差之和
    # 公式：
    # 供给方返还价差总和： ΣEp= profit * (1 - beta)
    # 申请电量价差总和: ΣEd = Σprice * power
    # 单参与方返还价差：Ep = ΣEp *  Ed/ ΣEd
    # 每度电价差波动： price = Ep/power = ΣEp * price / ΣEd
    for key in demander.keys(): r_d_d[key] = r_demander * demander[key][1] * (temp_d[key][0] - demander[key][0]) / total_demander
    for key in provider.keys(): r_p_d[key] = r_provider * provider[key][1] * (temp_p[key][0] - provider[key][0])/ total_provider
    # print(r_d_l, r_p_l,  profit * beta, profit * (1 - beta))
    for key in provider.keys():
        if temp_p[key][0] == provider[key][0]: continue
        provider[key][1] -= r_p_d[key]/(temp_p[key][0] - provider[key][0])
    for key in demander.keys():
        if temp_d[key][0] == demander[key][0]: continue
        demander[key][1] += r_d_d[key]/(temp_d[key][0] - demander[key][0])
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
        #profit = (temp_d[d_key][1] - demander[d_key][1]) * abs(demander[d_key][0])  #需求方收益
        # print(d_key, '节约支出', profit)
    for p_key in provider.keys():
        # profit = (provider[p_key][1] - temp_p[p_key][1]) * (temp_p[p_key][0] - provider[p_key][0])  #供给方价差之和
        profit = (provider[p_key][1] - temp_p[p_key][1]) * (temp_p[p_key][0] - provider[p_key][0])  #供给方价差之和
        #弃风弃电会有惩罚
        # profit -= provider[p_key]
        # print(p_key, '增加收益', profit)
        if p_key == 'B':
            # return  provider[p_key][1]
            return profit

if __name__ == '__main__':
   trade()
