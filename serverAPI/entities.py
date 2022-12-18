from typing import Dict, List, Set, Tuple

class Entities:
    nodeList:Dict[str, Set[str]] = dict()
    nextNodeList:Dict[str, Set[str]] = dict()
    nodeCheckResult:Dict[str,Dict[str, float]] = dict()
    
    cloudList:Dict[str, Set[str]] = dict()
    nextCloudList:Dict[str, Set[str]] = dict()
    cloudLastCheck:Dict[str,Dict[str, int]] = dict()
    cloudCheckResult:Dict[str,Dict[str,bool]] = dict()
    
    carPosList:Dict[str, Set[str]] = dict()
    nextCarPosList:Dict[str, Set[str]] = dict()
    carPosVetoCount:Dict[str,Dict[str, int]] = dict()
    carPosVoteCount:Dict[str,Dict[str, int]] = dict()
    posCheckResult:Dict[str,Dict[str, float]] = dict()

    negCheckResult:Dict[str,Dict[str,  float]] = dict()
    
    carCheckCount:Dict[str, int] = dict()
    
    nodeCredit:Dict[str,Dict[str, float]] = dict()
    
    testnum = 0