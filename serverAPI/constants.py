class Constant:
    # 超参数
    Basic = 5
    Basic1 = 2
    carThreshold = 10
    nodePercent = 20
    minPercent = 0.6

    # 地图信息和轮数信息，不是超参数
    size = 5
    dataGraphSize = 11
    carCount = 1000
    round = 30
    averageCheckTime = 8
    Credit0 = 100
    lastUpdate = 3
    
    # 暂时用不上的参数
    cloudThreshold = 5
    minPeriod = 4
    maxPeriod = 10
    t0 = -5
    penalty = 0.2

    # 额外的信息
    carPercent = 600

    # 样例生成信息


    # PSO超参数
    ByzantiumRatio = 0.6 # 修理成功是第一位的。
    RepairRatio = 0.5 # 认为现实中修理会更耽误时间，所以修复次数需要尽可能少。
    TimeRatio = 0.1 # 最后考虑修复时间，因为即使在现实，回合数也不会太长。

    
    
    DEFAULT_CHECK_RESULT = -1000
    
    
    
    @staticmethod
    def setConstant(b, b1, nodePer, minPer, carTh):
        Constant.Basic = int(b * Constant.Credit0)
        Constant.Basic1 = int(b1 * Constant.Credit0)
        Constant.nodePercent = int(nodePer * 100)
        Constant.minPercent = minPer
        Constant.carThreshold = int(carTh * 50)