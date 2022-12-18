from aelf_sdk import rsu_contract_pb2 as contract
from aelf_sdk.types_pb2 import Address
from aelf_sdk import AElf
from google.protobuf.wrappers_pb2 import StringValue
from google.protobuf.empty_pb2 import Empty
import base58
from protobuf_to_dict import protobuf_to_dict

class bc_plugin:
    def __init__(self, priKey, ip) -> None:
        self.aelfChain = AElf('http://'+ip)
        self._priKey = priKey
        self.contractAddress = str(
            "2LUmicHyH4RXrMjG4beDwuDsiWJESyLkgkwPdGTR8kahRzq5XS")

    def getTransactionResult(self, input):
        ret = self.aelfChain.get_transaction_result(input)

        formattedRet = dict()
        return ret

    def GetAdjInfo(self, input):
        transInput = Address()
        transInput.value = base58.b58decode_check(input)

        transaction = self.transConstructor(transInput, "GetAdjList")
        result = self.aelfChain.execute_transaction(transaction)
        
        ret = contract.NodeList()
        ret.ParseFromString(bytes.fromhex(result.decode()))
        formattedRet = protobuf_to_dict(ret)
        
        return formattedRet

    def transConstructor(self, input, function):
        transaction = self.aelfChain.create_transaction(
            self.contractAddress,
            function,
            input.SerializeToString()
        )
        transaction = self.aelfChain.sign_transaction(
            self._priKey, transaction)
        return transaction

    def NextRound(self, input):
        transInput = contract.RoundInfoInput()
        for node in input["NodeResult"].keys():
            transInput.NodeResult[node] = input["NodeResult"][node]
            
        for node in input["NodeList"]:
            addr = transInput.NodeList.Nodes.add()
            addr.value = base58.b58decode_check(node)

        for node in input["CloudList"]:
            addr = transInput.CloudList.Nodes.add()
            addr.value = base58.b58decode_check(node)
            
        for node in input["PositiveList"]:
            addr = transInput.PositiveList.Nodes.add()
            addr.value = base58.b58decode_check(node)
        
        transaction = self.transConstructor(transInput, "NextRound")
        result = self.aelfChain.send_transaction(
            transaction.SerializePartialToString().hex())

        print(result['TransactionId'])
        return result['TransactionId']

    def SystemInitialize(self):
        transaction = self.transConstructor(Empty(), "SystemInitialize")
        result = self.aelfChain.send_transaction(
            transaction.SerializePartialToString().hex())

        print(result['TransactionId'])
        return result['TransactionId']

    def UploadPositiveCheckResult(self):
        pass

    def UploadCloudCheckResult(self, input):
        transInput = contract.CloudCheckInput()
        transInput.To.value = base58.b58decode_check(input["To"])
        transInput.ServerSign = input["ServerSign"]
        transInput.DataHash = input["DataHash"]
        transInput.Result = input["Result"]
        transInput.Round = input["Round"]
        
        transaction = self.transConstructor(transInput, "UploadCloudCheckResult")
        result = self.aelfChain.send_transaction(
            transaction.SerializePartialToString().hex())

        print(result['TransactionId'])
        return result['TransactionId']

    def GetCheckResult(self):
        pass

    def GetStatus(self):
        transInput = Empty()
        transaction = self.transConstructor(transInput, "GetStatus")
        
        result = self.aelfChain.execute_transaction(transaction)
        
        ret = contract.StatusResult()
        ret.ParseFromString(bytes.fromhex(result.decode()))
        formattedRet = protobuf_to_dict(ret)
        return formattedRet
