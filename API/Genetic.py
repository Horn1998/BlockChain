from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import copy
DNA_SIZE = 24
POP_SIZE = 200
CROSSOVER_RATE = 0.8
MUTATION_RATE = 0.005
N_GENERATIONS = 200
def adjust(beta=0.25, power=0, price=0, address = 'B'):
    #下方为仿真数据
    block_index = 1
    provider = {'A': [1000, -400],  'B': [1500, -400], 'C': [2000, -300], 'D': [2000, -200]}
    demander = {'甲': [1500, -10], '乙': [1500, -20], '丙': [1000, -50], '丁': [3000, -100]}
    provider[address] = [power, price]

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
        # print(d_key, '节约支出', profit)
    for p_key in provider.keys():
        # profit = (provider[p_key][1] - temp_p[p_key][1]) * (temp_p[p_key][0] - provider[p_key][0])  #供给方价差之和
        profit = (provider[p_key][1] - temp_p[p_key][1]) * (temp_p[p_key][0] - provider[p_key][0])  #供给方价差之和
        #弃风弃电会有惩罚
        # profit -= provider[p_key]
        if p_key == address: return profit


def plot_3d(X_BOUND, Y_BOUND):
    Power = np.linspace(*X_BOUND, 100) #*list 将列表解开成单独的参数
    Price = np.linspace(*Y_BOUND, 100)
    Z, temp, minest, pow, pce = [], [], -1e9, 0, 0
    for power in Power:
        temp = []
        for price in Price:
            value = adjust(power=power, price=price)
            temp.append(value)
            if value > minest: minest, pow, pce = value, power, price
        Z.append(temp)
    Power, Price = np.meshgrid(Power, Price)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.view_init(elev=45, azim=45) #视角变换
    ax.plot_wireframe(np.array(Power), np.array(Price), np.array(Z))
    ax.set_xlabel('POWER')
    ax.set_ylabel('PRICE')
    ax.set_zlabel('PROPHIT')
    plt.show()
    print('最佳选择为功率', pow, '价格', pce)


def get_fitness(pop, X_BOUND, Y_BOUND):
    x, y = translateDNA(pop, X_BOUND, Y_BOUND)
    pred = []
    for i in range(POP_SIZE):
        pred.append(adjust(power=x[i], price=y[i]))
    pred = np.array(pred)
    return pred, np.max(pred)  # 减去最小的适应度是为了防止适应度出现负数，通过这一步fitness的范围为[0, np.max(pred)-np.min(pred)],最后在加上一个很小的数防止出现为0的适应度


#翻译*
def translateDNA(pop, X_BOUND, Y_BOUND):  # pop表示种群矩阵，一行表示一个二进制编码表示的DNA，矩阵的行数为种群数目
    x_pop = pop[:, 1::2]
    y_pop = pop[:, ::2]

    # pop:(POP_SIZE,DNA_SIZE)*(DNA_SIZE,1) --> (POP_SIZE,1)
    # x ,y = 新的光电，风电发电功率  float(2 ** DNA_SIZE - 1) * (X_BOUND[1] - X_BOUND[0]) 均分参数空间
    if X_BOUND[1] == X_BOUND[0]:
        x = np.array([X_BOUND[0] for _ in range(POP_SIZE)])
    else:
        x = x_pop.dot(2 ** np.arange(DNA_SIZE)[::-1]) / float(2 ** DNA_SIZE - 1) * (X_BOUND[1] - X_BOUND[0]) + X_BOUND[0]
    if Y_BOUND[1] == Y_BOUND[0]:
        y = np.array([Y_BOUND[0] for _ in range(POP_SIZE)])
    else:
        y = y_pop.dot(2 ** np.arange(DNA_SIZE)[::-1]) / float(2 ** DNA_SIZE - 1) * (Y_BOUND[1] - Y_BOUND[0]) + Y_BOUND[0]
    return x, y


#交叉编译*
def crossover_and_mutation(pop, CROSSOVER_RATE=0.8):
    new_pop = []
    for father in pop:  # 遍历种群中的每一个个体，将该个体作为父亲
        child = father  # 孩子先得到父亲的全部基因（这里我把一串二进制串的那些0，1称为基因）
        if np.random.rand() < CROSSOVER_RATE:  # 产生子代时不是必然发生交叉，而是以一定的概率发生交叉
            mother = pop[np.random.randint(POP_SIZE)]  # 再种群中选择另一个个体，并将该个体作为母亲
            cross_points = np.random.randint(low=0, high=DNA_SIZE * 2)  # 随机产生交叉的点
            child[cross_points:] = mother[cross_points:]  # 孩子得到位于交叉点后的母亲的基因
        mutation(child)  # 每个后代有一定的机率发生变异
        new_pop.append(child)

    return new_pop


#变异*
def mutation(child, MUTATION_RATE=0.003):
    if np.random.rand() < MUTATION_RATE:  # 以MUTATION_RATE的概率进行变异
        mutate_point = np.random.randint(0, DNA_SIZE)  # 随机产生一个实数，代表要变异基因的位置
        child[mutate_point] = child[mutate_point] ^ 1  # 将变异点的二进制为反转


#选择*
def select(pop, fitness):  # nature selection wrt pop's fitness
    idx = np.random.choice(np.arange(POP_SIZE), size=POP_SIZE, replace=True,
                           p=(fitness) / (fitness.sum()))
    return pop[idx]


def run(POWER_BOUND, PRICE_BOUND):
    #确定初始种群（0，1二进制编码） pop[200, 48]
    pop = np.random.randint(2, size=(POP_SIZE, DNA_SIZE * 2))  # matrix (POP_SIZE, DNA_SIZE)
    #记录优化结果
    x, y, max_fitness_index, answer = None, None, None, []
    #遗传算法
    for gener in range(N_GENERATIONS):  # 迭代N代
        pop = np.array(crossover_and_mutation(pop, CROSSOVER_RATE))
        fitness, _ = get_fitness(pop, POWER_BOUND, PRICE_BOUND)
        pop = select(pop, fitness)  # 选择生成新的种群
        fitness, pred = get_fitness(pop, POWER_BOUND, PRICE_BOUND)
        answer.append(pred)
        max_fitness_index = np.argmax(fitness)
        x, y = translateDNA(pop, POWER_BOUND, PRICE_BOUND)

        if gener == N_GENERATIONS - 1:
            print(pred, '遗传算法计算结果power', x[max_fitness_index], ';    price', y[max_fitness_index])
    plot_3d(POWER_BOUND, PRICE_BOUND)

    #展示遗传算法优化过程
    x = [i for i in range(N_GENERATIONS)]
    plt.plot(x, answer)
    plt.show()
    return x[max_fitness_index], y[max_fitness_index], np.max(answer)


if __name__ == "__main__":
    run([500, 3000], [-140, -100])



















