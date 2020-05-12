import sys
import random

from optparse import OptionParser
from collections import defaultdict
from itertools import chain, combinations

global lenOfTList
minSupport = 0
minConfidence = 0
developNum = 100
global allData
itemCount = dict()
pcl =0.6
pch =0.95
pm = 0.4
def runApriori_genetic(data_iter):
    """
    run the apriori algorithm. data_iter is a record iterator
    Return both:
     - items (tuple, support)
     - rules ((pretuple, posttuple), confidence)
    """
    global allData
    global lenOfTList
    """itemSet是所有一项的集，transaction LIst是所有多项集的列表"""
    itemSet, transactionList = getItemSetTransactionList(data_iter)
    allData = transactionList
    lenOfTList = allData.__len__()
    """freqSet存储的是所有符合最小支持度的项集的出现次数，largeSet存储的是满足最下支持度的频繁项集"""
    freqSet = defaultdict(int)
    largeSet = dict()
    """从这里开始用遗传算法进行频繁项集的挖掘，首先我们定义一个200的种群，个体是一个数组，里面用0和1，表示该项是否出现，长度为当前阶项集的个数。获取的是所有频繁项集"""
    itemSet = list(itemSet)
    """我们应当首先获取频繁一项集，然后导入"""
    freItemOneSet = getOne(itemSet,transactionList)
    """然后把频繁一项集代入运算中"""
    items,rules=genetic(freItemOneSet)
    return items,rules




def printResults(items, rules):
    """prints the generated itemsets sorted by support and the confidence rules sorted by confidence"""
    support = ''
    confidence = ''
    for item, support in sorted(items, key=lambda item_support: support):
        print("item: %s , %.3f" % (str(item), support))
    print("\n------------------------ RULES:")
    for rule, confidence in sorted(rules, key=lambda rule_confidence: confidence):
        pre, post = rule
        print ("Rule: %s ==> %s , %.3f" % (str(pre), str(post), confidence))

"""频繁一项集合获取函数"""
def getOne(item,tList):
    """"""
    """这里是获取频繁一项集合的"""
    i = 0
    newList = list()
    while i< item.__len__():
        num = 0
        for items in tList:
            if item[i].issubset(items):
                num = num + 1
        if num/tList.__len__() > minSupport:
            newList.append(item[i])
        i=i+1
    return  newList




def genetic(itemSet):
    """<>"""
    """这是一个循环，每次循环会得到k阶的频繁项集，从1阶开始，然后判断项集是否符合要求，如果不符合，将不会进行k+1阶的频繁项集搜索"""
    """对于一个个体的适应度函数计算，支持度部分，采用所有单个项支持度的平均值作为该个体的支持度，置信度部分，则检测是否有强关联规则在其中，如果支持度不满足，则置信度不计算"""
    """由于选择函数容易淘汰过多的参数，在多次迭代后会产生局部最优化问题，在第一次尝试中，我们产生一半（选择后个体数量）的子代进行概率选择"""
    """newSet保存的是当前阶次所有项集"""
    needContinue = True
    k = 2
    newSet = itemSet
    largeSet = dict()
    while needContinue:
        """先生成初始种群,获取初始种群并获取新一代序列"""
        """seedList保存当前阶所有项集，list保存种群"""
        seedList,liSt = createBeginSpecial(newSet,k)
        if seedList.__len__()==0:
            break
        i = 0
        while i < developNum:
            print(i)
            """然后开始选择,originalList保存的是一开始的种群，list保存算法处理后的种群"""
            """保证个体数量"""
            if liSt.__len__() <200:
                a = random.randint(0,liSt.__len__()-1)
                b = 0
                while b<200-liSt.__len__():
                    liSt.append(liSt[a])
                    b = b + 1
            originalList = liSt
            liSt = select(seedList,originalList)
            """在这里开始交叉"""
            liSt = crossover(originalList,liSt)
            """开始变异"""
            liSt = mutate(originalList,liSt)
            i = i+1
        j = 0
        supList, conList = calRate(seedList, liSt)
        max = 0
        local = 0
        while j<liSt.__len__():
            if supList[j]+conList[j]>max:
                max = supList[j]+conList[j]
                local = j
            j = j + 1
        newDealList = liSt[local]
        j = 0
        nextLiSt =list()
        while j<newDealList.__len__():
            if newDealList[j]==1:
                nextLiSt.append(seedList[j])
            j = j + 1
        if i == 40:
            print(liSt.__len__())
        newSet =nextLiSt
        largeSet[k] = newSet
        print(largeSet[k])
        k = k + 1

    """寻求解决"""
    print(largeSet)
    print(itemCount)
    toRetItems = []
    for key, value in largeSet.items():
        for item in value:
            if getSupport(item)>= minSupport:
                toRetItems.extend([(tuple(item), getSupport(item))])

    toRetRules = []
    for key, value in list(largeSet.items()):
        for item in value:
            """获得单个k次频繁项的所有子集的迭代器"""
            """排除自身，计算某个子集的置信度，如果超过定额，则该子集及其补集存入toRetRules中"""
            _subsets = map(frozenset, [x for x in subsets(item)])
            for element in _subsets:
                remain = item.difference(element)
                if len(remain) > 0:
                    confidence = getSupport(item) / getSupport(element)
                    if confidence >= minConfidence:
                        toRetRules.append(((tuple(element), tuple(remain)),
                                           confidence))
    return toRetItems,toRetRules






def mutate(getList,returnList):
    """"""
    """每一个物种都有变异机会，"""
    i = 0
    while i<getList.__len__():
        a = random.random()
        if a>pm:
            list = getList[i]
            b = random.randint(0,list.__len__()-1)
            c = random.randint(0,list.__len__()-1)
            if list[b] == 0:
                list[b] =1
            else:
                list[b]=0
            if list[c] == 0:
                list[c]=1
            else:
                list[c]=0
            returnList.append(list)
        i = i + 1
    return returnList



def crossover(getList,returnList):
    """"""
    """我采取的是选择父代i和i+1的个体，各取一半生成新个体，然后概率添加到新一代中,保证200个体"""
    len = getList[0].__len__()
    i = 0
    if getList.__len__()>200:
        return getList[:200]
    while i < getList.__len__()-1:
        ra = random.random()
        if ra>pcl and ra<pch:
            a = list()
            j = 0
            while j < len/2:
                a.append(getList[i][j])
                j = j + 1
            while j < len:
                a.append(getList[i+1][j])
                j = j + 1
            returnList.append(a)
        i = i + 2
    return returnList







def select(newSet,getList):
    """"""
    """选择函数，将所有符合适应度函数要求的个体保留下来"""
    supportList,confidentList =calRate(newSet,getList)
    i = 0
    newList = list()
    while i<getList.__len__():
        if supportList[i]>1:
            if confidentList[i] > 1:
                newList.append(getList[i])
        i = i + 1
    return newList


def calRate(newSet,getList):
    """"""
    """这是适应度的计算,返回一个个体适应度的列表，包括支持度和置信度列表"""
    perCal = list()
    conList = list()
    i = 0
    while i < getList.__len__():
        ans1,ans2 = supportCount(newSet,getList[i])
        perCal.append(ans1)
        conList.append(ans2)

        i = i + 1
    return   perCal, conList








def supportCount(newSet,list):
    """"""
    """这里是计算个体适应度的,计算每一个项的支持度,如果支持度满足最小条件，则计算置信度"""
    """对于一个个体，要求其标1的平均支持度比上最小支持度，再用平均置信度比上最小置信度"""
    i = 0
    sup = 0
    con = 0
    icount = 0
    while i < list.__len__():
        if(list[i]==1):
            icount = icount + 1
            sup = sup + getSupport(newSet[i])
            con = con + getConfident(newSet[i])
        i = i+1
    if(icount==0):
        return 0,0
    return (sup/icount)/minSupport,(con/icount)/minConfidence


def getSupport(item):
    global allData
    item = tuple(item)
    if item in itemCount:
        return itemCount[item]
    else:
        count = 0
        for k in allData:
            if set(item).issubset(k):
                count = count + 1
        itemCount[item] = float(count)/allData.__len__()
    return itemCount[item]


def getConfident(item):
    """"""
    """置信度取该项集中最高值"""
    item = set(item)
    _subsets = map(frozenset, [x for x in subsets(item)])
    max = 0
    for element in _subsets:
        remain = item.difference(element)
        if len(remain) > 0:
            if element.__len__() >0:
                confidence = getSupport(item) / getSupport(element)
            if confidence > max:
                max = confidence
    return max



def subsets(arr):
    """ Returns non empty subsets of arr"""
    """返回所有子集的迭代器"""
    return chain(*[combinations(arr, i + 1) for i, a in enumerate(arr)])

def joinSet(itemSet, length):
    """Join a set with itself and returns the n-element itemsets"""
    """获取k项集"""
    return set([i.union(j) for i in itemSet for j in itemSet if len(i.union(j)) == length])



def createBeginSpecial(getList,k):
    """"""
    """getList里面是所有上代，要先生成下一阶项集"""
    need = set(getList)
    getList = list(joinSet(need,k))
    """返回初始种群"""
    i = 0
    special = list()
    while i < 200:
        a = getList.__len__()
        temp = list()
        while a > 0:
            temp.append(random.choice([0, 1]))
            a = a-1
        special.append(temp)
        i = i + 1
    return getList,special








def getItemSetTransactionList(data_iterator):
    transactionList = list()
    itemSet = set()
    """将文件中的数据按照项集封装在一个冻结的集合里，然后添加到列表中，再使用set()将重复的项去除，得到所有的项"""
    for record in data_iterator:
        transaction = frozenset(record)
        transactionList.append(transaction)
        for item in transaction:
            itemSet.add(frozenset([item]))              # Generate 1-itemSets
    """返回第一个是所有一次项的集，第二个是所有多项集的列表"""
    return itemSet, transactionList


def returnItemsWithMinSupport(itemSet, transactionList, minSupport, freqSet):
    """calculates the support for items in the itemSet and returns a subset
   of the itemSet each of whose elements satisfies the minimum support"""
    _itemSet = set()
    localSet = defaultdict(int)
    """计算k次项在多项集中出现的次数"""
    for item in itemSet:
        for transaction in transactionList:
            if item.issubset(transaction):
                freqSet[item] += 1
                localSet[item] += 1
        """计算k次项在多项集中出现的频率，并与最小支持度进行比较，符合要求的存入新的set()中，并返回"""
    for item, count in localSet.items():
        support = float(count) / len(transactionList)

        if support >= minSupport:
            _itemSet.add(item)

    return _itemSet


def dataFromFile(fname):
    """Function which reads from the file and yields a generator"""
    """读取文件，传递构造器"""
    file_iter = open(fname, 'r',encoding='UTF-8')
    for line in file_iter:
        line = line.strip().rstrip(',')  # Remove trailing comma
        record = frozenset(line.split(','))
        yield record

def printResults(items, rules):
    """prints the generated itemsets sorted by support and the confidence rules sorted by confidence"""
    support = ''
    confidence = ''
    for item, support in sorted(items, key=lambda item_support: support):
        print("item: %s , %.3f" % (str(item), support))
    print("\n------------------------ RULES:")
    for rule, confidence in sorted(rules, key=lambda rule_confidence: confidence):
        pre, post = rule
        print ("Rule: %s ==> %s , %.3f" % (str(pre), str(post), confidence))


if __name__ == "__main__":
    """
提取命令行参数 ，获取数据文件所在位置以及置信度支持度
    """
    optparser = OptionParser()
    optparser.add_option('-f', '--inputFile',
                         dest='input',
                         help='filename containing csv',
                         default=None)
    optparser.add_option('-s', '--minSupport',
                         dest='minS',
                         help='minimum support value',
                         default=0.15,
                         type='float')
    optparser.add_option('-c', '--minConfidence',
                         dest='minC',
                         help='minimum confidence value',
                         default=0.6,
                         type='float')
    testargs = ['-f', 'test_01.csv', '-s', '0.22', '-c', '0.7']
    (options, args) = optparser.parse_args(testargs)


    inFile = None
    if options.input is None:
            inFile = sys.stdin
    elif options.input is not None:
            inFile = dataFromFile(options.input)
    else:
            print ('No dataset filename specified, system with exit\n')
            sys.exit('System will exit')

    minSupport = options.minS
    minConfidence = options.minC
    items, rules = runApriori_genetic(inFile)
    print('print rules')
    printResults(items, rules)



