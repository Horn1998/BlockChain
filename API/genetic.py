import numpy as np
import matplotlib.pyplot as plt
from API.Concentrated import adjust
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
DNA_SIZE = 24
POP_SIZE = 200
CROSSOVER_RATE = 0.8
MUTATION_RATE = 0.005
N_GENERATIONS = 200


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
    answer = []
    #遗传算法
    for gener in range(N_GENERATIONS):  # 迭代N代
        pop = np.array(crossover_and_mutation(pop, CROSSOVER_RATE))
        fitness, _ = get_fitness(pop, POWER_BOUND, PRICE_BOUND)
        pop = select(pop, fitness)  # 选择生成新的种群
        fitness, pred = get_fitness(pop, POWER_BOUND, PRICE_BOUND)
        answer.append(pred)
        np.argmax(fitness)
        x, y = translateDNA(pop, POWER_BOUND, PRICE_BOUND)
        if gener == N_GENERATIONS - 1: print('遗传算法计算结果power', x[0], ';    price', y[0])
    plot_3d(POWER_BOUND, PRICE_BOUND)

    #展示遗传算法优化过程
    x = [i for i in range(N_GENERATIONS)]
    plt.plot(x, answer)
    plt.show()






















