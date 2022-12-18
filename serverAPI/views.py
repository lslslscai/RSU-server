from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from serverAPI.bc_plugin import bc_plugin
from serverAPI import models
from topserver.settings import SELF_INFO
from django.utils import timezone
import asyncio
from serverAPI.entities import Entities
from serverAPI.constants import Constant
from serverAPI.helpers import Helpers
from typing import Dict, List, Set, Tuple
import requests
import json
import pymysql
import hashlib

# Create your views here.


def manualCloudCheck(req: HttpRequest) -> HttpResponse:
    node = models.NodeInfo.objects.filter(
        address=req.POST.get("address")
    )[0]
    url = "http://"+node.host+"/cloud/reqCloudCheck"
    data = {
        "host": req.get_host()
    }
    selfInfo = models.SelfInfo.objects.get()
    handler = handler = bc_plugin(SELF_INFO.get("private_key"),
                                  req.POST.get("bc_endpoint"))
    status = handler.GetStatus()
    print(status, selfInfo.current_round)
    requests.post(url, data)
    return HttpResponse("ok")


def cloudCheck(req: HttpRequest) -> HttpResponse:
    selfInfo = models.SelfInfo.objects.get()
    nodeInfo = models.NodeInfo.objects.filter(
        address=req.POST.get("address"))[0]
    areaInfo = models.AreaInfo.objects.filter(chainID=nodeInfo.chain_id)[0]
    dataSet = json.loads(req.POST.get("dataSet"))
    db = pymysql.connect(host="bj-cdb-0tslvdym.sql.tencentcdb.com",
                         port=59568, user="root", password="tjubc12345", database="clouddb")
    cursor = db.cursor()
    string = ""
    flag = True
    for i in dataSet:
        sql = """
            select * from data where
            loc_x = {} and
            loc_y = {} and
            type = {} and
            data_hash = "{}" and
            content = "{}" and
            create_round = {};
        """.format(
            i["loc_x"],
            i["loc_y"],
            i["type"],
            i["data_hash"],
            i["content"],
            i["create_round"]
        )
        cursor.execute(sql)
        res = cursor.fetchall()
        if len(res) == 0:
            flag = False
            break
        string += i["content"]
    dataHash = hashlib.sha256(string.encode()).hexdigest()
    input = {
        "DataHash": dataHash,
        "To": req.POST.get("address"),
        "ServerSign": SELF_INFO.get("address"),
        "Result": flag,
        "Round": selfInfo.current_round
    }
    print(input)
    handler = bc_plugin(SELF_INFO.get("private_key"), areaInfo.bc_endpoint)
    handler.UploadCloudCheckResult(input)

    Entities.cloudCheckResult[req.POST.get(
        "chain_id")][nodeInfo.address] = flag
    return HttpResponse("ok")


def getCheckResult(req: HttpRequest) -> HttpResponse:
    print("getCheckResult!"+req.POST.get("address"))
    selfInfo = models.SelfInfo.objects.get()
    info = models.CheckPoint.objects.filter(
        chain_id=req.POST.get("chain_id"),
        owner=req.POST.get("address"),
        round=selfInfo.current_round
    )
    if len(info) == 0:
        return HttpResponse(-1000)

    return HttpResponse(info[0].result)


def areaInitialize(req: HttpRequest) -> HttpResponse:
    handler = bc_plugin(SELF_INFO.get("private_key"),
                        req.POST.get("bc_endpoint"))
    handler.SystemInitialize()
    id = handler.aelfChain.get_chain_id()
    info = models.AreaInfo(
        chainID=id,
        bc_endpoint=req.POST.get("bc_endpoint")
    )
    info.save()

    Helpers.EntitiesInit(str(id))
    return HttpResponse("ok")


def initialize(req: HttpRequest) -> HttpResponse:
    if not len(models.SelfInfo.objects.all()) == 0:
        return HttpResponse("already initialized!")
    nodeInfo = models.SelfInfo(
        address=SELF_INFO.get("address"),
        private_key=SELF_INFO.get("private_key"),
        bc_port=SELF_INFO.get("bc_port"),
        current_round=0
    )

    nodeInfo.save()
    return HttpResponse("ok")


def getAdjList(req: HttpRequest) -> HttpResponse:
    selfInfo = models.SelfInfo.objects.get()
    handler = bc_plugin(selfInfo.private_key, req.POST.get("bc_endpoint"))
    print(handler.GetAdjInfo(req.POST.get("address")))
    return HttpResponse("ok")


def start(req: HttpRequest) -> HttpResponse:
    areaInfo = models.AreaInfo.objects.all()
    selfInfo = models.SelfInfo.objects.get()
    task = []
    for area in areaInfo:
        handler = bc_plugin(SELF_INFO.get("private_key"), area.bc_endpoint)
        nodeInfos = models.NodeInfo.objects.filter(chain_id=area.chainID)

        Helpers.calRoundResult(area.chainID, selfInfo.current_round)
        input = {
            "NodeList": list(Entities.nextNodeList[area.chainID]),
            "CloudList": list(Entities.nextCloudList[area.chainID]),
            "PositiveList": list(Entities.nextCarPosList[area.chainID]),
            "NodeResult": dict()
        }

        # Entities.nextNodeList[area.chainID].add(
        #     "2vU96cFUEpLyUPnChizTaks52d8KcFra8WfE1XUji5txzRacDw")
        # Entities.nextNodeList[area.chainID].add(
        #     "2KBWT39ZCzL19Z7VA5adkzf8SrLqQZ7nXByiMmUVXobekNWHMH")
        # Entities.nextCloudList[area.chainID].add(
        #     "2KBWT39ZCzL19Z7VA5adkzf8SrLqQZ7nXByiMmUVXobekNWHMH")
        # input = {
        #     "NodeList": [
        #         "2vU96cFUEpLyUPnChizTaks52d8KcFra8WfE1XUji5txzRacDw",
        #         "2KBWT39ZCzL19Z7VA5adkzf8SrLqQZ7nXByiMmUVXobekNWHMH"
        #     ],
        #     "CloudList": [
        #         "2KBWT39ZCzL19Z7VA5adkzf8SrLqQZ7nXByiMmUVXobekNWHMH"
        #     ],
        #     "PositiveList": [],
        #     "NodeResult": {}
        # }
        for k, v in Entities.nodeCheckResult[area.chainID].items():
            if k in Entities.nodeList[area.chainID]:
                input["NodeResult"][k] = int(10**5 * v)
        print(input)

        Helpers.update(area.chainID, selfInfo.current_round+1)
        handler.NextRound(input)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        Helpers.startNodeCheck(task, nodeInfos)
    print(task)

    loop.run_until_complete(asyncio.wait(task))
    task = []
    selfInfo.current_round += 1
    selfInfo.save()
    # status = handler.GetStatus()
    # print(status, selfInfo.current_round)

    for area in areaInfo:
        nodeInfos = models.NodeInfo.objects.filter(chain_id=area.chainID)

        for node in nodeInfos:
            if node.address in Entities.cloudList[area.chainID]:
                print("in!X!")
                Helpers.startCloudCheck(task, node, req.get_host())
            if node.last_update >= Constant.lastUpdate:
                print("in!Y!")
                node.last_update = 0
                Helpers.startUpload(task, node)
            else:
                node.last_update += 1
            node.save()
    print(task)
    if len(task) > 0:
        loop.run_until_complete(asyncio.wait(task))

    selfInfo.save()
    return HttpResponse("ok")


def nodeRegister(req: HttpRequest) -> HttpResponse:
    # Helpers.nodeInit(req.POST.get("chain_id"),req.POST.get("address"))
    currTime = timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
    if not len(models.NodeInfo.objects.filter(address=req.POST.get("address"))) == 0:
        return HttpResponse("server: serverException! already initialized!")

    try:
        nodeInfo = models.NodeInfo(
            reg_time=currTime[0],
            address=req.POST.get("address"),
            private_key=req.POST.get("private_key"),
            loc_x=req.POST.get("loc_x"),
            loc_y=req.POST.get("loc_y"),
            chain_id=req.POST.get("chain_id"),
            host=req.POST.get("host"),
            credit=Constant.Credit0
        )
        nodeInfo.save()
        Helpers.nodeInit(req.POST.get("chain_id"), req.POST.get("address"))
        return HttpResponse("server:#"+str(currTime[0])+"#"+SELF_INFO.get("address"))
    except Exception as e:
        return HttpResponse("server: serverException!\n"+str(e))


def collectCarNegResult(req: HttpRequest) -> HttpResponse:
    # 检查检查者与被检查者存在性
    node = models.NodeInfo.objects.filter(address=req.POST.get("node_address"))
    car = models.CarInfo.objects.filter(address=req.POST.get("car_address"))
    if len(node) == 0 or len(car) == 0:
        return HttpResponse("invalid neg check!")

    # 更改汽车投票次数，并计算票权
    result = Helpers.calculateCarWeight(car[0].address, req.POST.get("result"))

    # 票权加入结果中
    if not node[0].address in Entities.negCheckResult:
        Entities.negCheckResult[node[0].address] = result
    else:
        Entities.negCheckResult[node[0].address] += result

    return HttpResponse("ok")


def collectCarPosResult(req: HttpRequest) -> HttpResponse:
    # 检查检查者与被检查者存在性，以及是否需要被检查
    node = models.NodeInfo.objects.filter(address=req.POST.get("node_address"))
    car = models.CarInfo.objects.filter(address=req.POST.get("car_address"))
    if len(node) == 0 or len(car) == 0 or (not node[0].address in Entities.carPosList):
        return HttpResponse("invalid pos check!")

    # 更改汽车投票次数，并计算票权
    result = Helpers.calculateCarWeight(car[0].address, req.POST.get("result"))

    # 票权加入结果中
    if not node[0].address in Entities.posCheckResult:
        Entities.posCheckResult[node[0].address] = result
    else:
        Entities.posCheckResult[node[0].address] += result

    # 记录总数量与反对票数量
    if not node[0].address in Entities.carPosVoteCount:
        Entities.carPosVoteCount[node[0].address] = 1
    else:
        Entities.carPosVoteCount[node[0].address] += 1
    if result < 0:
        if not node[0].address in Entities.carPosVetoCount:
            Entities.carPosVetoCount[node[0].address] = 1
        else:
            Entities.carPosVetoCount[node[0].address] += 1
    return HttpResponse("ok")


def carRegister(req: HttpRequest) -> HttpResponse:
    pass


def collectNodeResult(req: HttpRequest) -> HttpResponse:
    print(req.POST)
    # 查看检查者和被检查者身份，以及节点是否需要被检查
    chain_id = req.POST.get("chain_id")
    checker = models.NodeInfo.objects.filter(
        address=req.POST.get("checker_address"))
    checked = models.NodeInfo.objects.filter(
        address=req.POST.get("checked_address"))
    print(req.POST.get("checked_address"), req.POST.get("checker_address"))
    if len(checker) == 0 or len(checked) == 0 or (not checked[0].address in Entities.nodeList[chain_id]):
        return HttpResponse("invalid pos check!")

    # 计算票权
    result = Helpers.calculateNodeWeight(
        checker[0].address, req.POST.get("result"), chain_id)

    print(
        "before:"+str(Entities.nodeCheckResult[chain_id][checked[0].address]))
    # 将票权加入结果
    if Entities.nodeCheckResult[chain_id][checked[0].address] == Constant.DEFAULT_CHECK_RESULT:
        Entities.nodeCheckResult[chain_id][checked[0].address] = result
    else:
        Entities.nodeCheckResult[chain_id][checked[0].address] += result
    print("after:"+str(Entities.nodeCheckResult[chain_id][checked[0].address]))

    return HttpResponse("ok")
