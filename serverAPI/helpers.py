from serverAPI.entities import Entities
from serverAPI.constants import Constant
import aiohttp
import random
import asyncio
from serverAPI import models
from time import time
from typing import List
from serverAPI.constants import Constant


class Helpers:
    @staticmethod
    async def callNodeCheck(host):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=host+"/sys/startRound") as response:
                html = await response.text()
                print(html)

    @staticmethod
    async def callCloudCheck(host, dest):
        async with aiohttp.ClientSession() as session:
            async with session.post(url=dest+"/cloud/reqCloudCheck", data={"host": host}) as response:
                html = await response.text()
                print(html)

    @staticmethod
    async def callUpload(dest):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=dest+"/data/uploadLongTermData") as response:
                html = await response.text()
                print(html)
    
    @staticmethod
    def startNodeCheck(task: List, nodeInfos):
        for node in nodeInfos:
            t = asyncio.ensure_future(
                Helpers.callNodeCheck("http://"+node.host))
            task.append(t)

    @staticmethod
    def startCloudCheck(task: List, node, host):
        t = asyncio.ensure_future(Helpers.callCloudCheck(host, "http://"+node.host))
        task.append(t)

    @staticmethod
    def startUpload(task: List, node):
        t = asyncio.ensure_future(Helpers.callUpload("http://"+node.host))
        task.append(t)

    @staticmethod
    def generateCheckList(chainID):
        random.seed(random.randint(1, 1000))
        nodes = models.NodeInfo.objects.all()
        # 按原流程抽选下一轮的云端和节点检查列表
        for node in nodes:
            # 按照一定比例抽取，随机抽取
            rand = random.randint(1, 100)
            if rand < Constant.nodePercent and len(Entities.nodeList[chainID]) <= len(nodes)/2:
                Entities.nodeList[chainID].add(node.address)

    @staticmethod
    def calculateCarWeight(carAddr, result):
        if not carAddr in Entities.carCheckCount:
            Entities.carCheckCount[carAddr] = 1
        else:
            Entities.carCheckCount[carAddr] += 1

        # 计算票权
        ret = Constant.carThreshold / \
            max(Entities.carCheckCount[carAddr], Constant.carThreshold)
        if result == "2":
            ret *= -1
        return ret

    @staticmethod
    def calculateNodeWeight(nodeAddr, result, chainID):
        ret = Entities.nodeCredit[chainID][nodeAddr]
        if result == False:
            ret *= -1
        return ret

    @staticmethod
    def calCreditPercent(nodes) -> float:
        sum = 0
        for node in nodes:
            sum += node.credit

        return sum / (len(nodes) * Constant.Credit0)

    @staticmethod
    def calRoundResult(chainID, round):
        # 准备修改数据库
        nodes = models.NodeInfo.objects.filter(chain_id=chainID)
        random.seed(time())
        print(Entities.nextCarPosList)
        print(Entities.nextNodeList)
        print(Entities.nextCloudList)
        for node in nodes:
            # 第一回合开始前不统计上一回合校验结果
            if not round == 0:
                # 如果需要进行检查，才确认结果
                # 根据检查结果，调整可信值，并根据设定将其纳入下一轮检查列表。
                if node.address in Entities.nodeCheckResult[chainID]:
                    if Entities.nodeCheckResult[chainID][node.address] > 0:
                        Helpers.recoverNode(node, round)
                    elif not Entities.nodeCheckResult[chainID][node.address] == Constant.DEFAULT_CHECK_RESULT:
                        Helpers.nodePenalty(node, nodes, chainID)

                if node.address in Entities.posCheckResult[chainID]:
                    if Entities.posCheckResult[chainID][node.address] > 0:
                        Helpers.recoverCar(node)
                    elif not Entities.posCheckResult[chainID][node.address] == Constant.DEFAULT_CHECK_RESULT:
                        Helpers.carPenalty(node, chainID)

                if node.address in Entities.cloudCheckResult[chainID]:
                    if Entities.cloudCheckResult[chainID][node.address]:
                        Helpers.recoverCloud(node)
                    elif not Entities.cloudCheckResult[chainID][node.address] == Constant.DEFAULT_CHECK_RESULT:
                        Helpers.cloudPenalty(node, chainID)

                if Entities.negCheckResult[chainID][node.address] <= 0 and\
                        not Entities.negCheckResult[chainID][node.address] == Constant.DEFAULT_CHECK_RESULT:
                    Entities.nextNodeList[chainID].add(node.address)
            # 随机挑选参与云端和节点检查
            if random.randint(1, 100) < Constant.nodePercent and len(Entities.nextNodeList[chainID]) <= len(nodes)/2:
                Entities.nextNodeList[chainID].add(node.address)
            if (random.randint(1, 100) < Constant.cloudThreshold and Entities.cloudLastCheck[chainID][node.address] > Constant.minPeriod) \
                    or Entities.cloudLastCheck[chainID][node.address] > Constant.maxPeriod:
                Entities.nextCloudList[chainID].add(node.address)
                Entities.cloudLastCheck[chainID][node.address] = 0
            if not node.address in Entities.nextCloudList[chainID]:
                Entities.cloudLastCheck[chainID][node.address] += 1

            # 结果写入数据库
            node.save()
        print(Entities.nextCarPosList)
        print(Entities.nextNodeList)
        print(Entities.nextCloudList)

    @staticmethod
    def update(chainID, round):
        # 清空上一轮列表
        Entities.nodeList[chainID].clear()
        Entities.nodeCheckResult[chainID].clear()

        Entities.cloudList[chainID].clear()
        Entities.cloudCheckResult[chainID].clear()

        Entities.carPosList[chainID].clear()
        Entities.carPosVetoCount[chainID].clear()
        Entities.carPosVoteCount[chainID].clear()
        Entities.posCheckResult[chainID].clear()

        # 将下一轮新值赋到本轮位置
        for i in Entities.nextNodeList[chainID]:
            Entities.nodeList[chainID].add(i)
            Entities.nodeCheckResult[chainID][i] = Constant.DEFAULT_CHECK_RESULT
            checkPt = models.CheckPoint(
                chain_id=chainID,
                owner=i,
                round=round,
                result=0,
            )
            checkPt.save()

        for i in Entities.nextCloudList[chainID]:
            Entities.cloudList[chainID].add(i)
            Entities.cloudCheckResult[chainID][i] = True

        for i in Entities.nextCarPosList[chainID]:
            Entities.carPosList[chainID].add(i)
            Entities.carPosVetoCount[chainID][i] = 0
            Entities.carPosVoteCount[chainID][i] = 0
            Entities.posCheckResult[chainID][i] = Constant.DEFAULT_CHECK_RESULT

        for i in Entities.negCheckResult[chainID].values():
            i = Constant.DEFAULT_CHECK_RESULT

        Entities.nextNodeList[chainID].clear()
        Entities.nextCloudList[chainID].clear()
        Entities.nextCarPosList[chainID].clear()

    @staticmethod
    def nodeInit(chainID, address):
        Entities.cloudLastCheck[chainID][address] = 0
        Entities.negCheckResult[chainID][address] = Constant.DEFAULT_CHECK_RESULT
        Entities.nodeCredit[chainID][address] = Constant.Credit0

    @staticmethod
    def carInit(address):
        Entities.carCheckCount[address] = 0

    @staticmethod
    def EntitiesInit(chainID: str):
        Entities.nodeList[chainID] = set()
        Entities.nodeCheckResult[chainID] = dict()
        Entities.nextNodeList[chainID] = set()

        Entities.cloudList[chainID] = set()
        Entities.cloudCheckResult[chainID] = dict()
        Entities.cloudLastCheck[chainID] = dict()
        Entities.nextCloudList[chainID] = set()

        Entities.carPosList[chainID] = set()
        Entities.carPosVetoCount[chainID] = dict()
        Entities.carPosVoteCount[chainID] = dict()
        Entities.posCheckResult[chainID] = dict()
        Entities.nextCarPosList[chainID] = set()

        Entities.negCheckResult[chainID] = dict()
        Entities.nodeCredit[chainID] = dict()
        print(chainID, chainID in Entities.nodeList)

    @staticmethod
    def recoverNode(n: models.NodeInfo, round):
        n.credit += 0.2*(Constant.Credit0 - n.credit)
        checkPt = models.CheckPoint.objects.filter(
            chain_id=n.chain_id,
            owner=n.address,
            round=round
        )[0]
        checkPt.result = 1
        checkPt.save()

    @staticmethod
    def recoverCar(n: models.NodeInfo):
        n.credit += 0.05*(Constant.Credit0 - n.credit)

    @staticmethod
    def recoverCloud(n: models.NodeInfo):
        n.credit += 0.1*(Constant.Credit0 - n.credit)

    @staticmethod
    def nodePenalty(n: models.NodeInfo, nodes, chainID):
        percent = Helpers.calCreditPercent(nodes)
        n.credit = max(0, n.credit - Constant.Basic * percent)
        Entities.nextCarPosList[chainID].add(n.address)

    @staticmethod
    def carPenalty(n: models.NodeInfo, chainID):
        percent = Entities.carPosVetoCount[n.address] / \
            Entities.carPosVoteCount[n.address]
        n.credit = max(0, n.credit - Constant.Basic1 * percent)
        Entities.nextNodeList[chainID].add(n.address)

    @staticmethod
    def cloudPenalty(n: models.NodeInfo, chainID):
        n.credit *= (1-Constant.penalty)
        Entities.nextCloudList[chainID].add(n.address)
