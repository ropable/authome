from multiprocessing import Process,Pipe
import traceback
import time
import random
import json
import collections
from datetime import datetime,timedelta

from django.test import TestCase
from django.utils import timezone
from django.conf import settings
from django.core.cache import caches

from . import utils


class DataMismatchException(Exception):
    pass

class RedisClusterTestCase(TestCase):
    TEST_REDISCLUSTER_CACHE = utils.env("TEST_REDISCLUSTER_CACHE",default="default")
    TEST_KEYS_PER_GROUP = utils.env("TEST_KEYS_PER_GROUP",default=1000)
    TEST_PROCESSES_PER_GROUP = utils.env("TEST_PROCESSES_PER_GROUP",default=2)
    REQUEST_INTERVAL = utils.env("REQUEST_INTERVAL",default=1) #milliseconds
    TEST_TIME = utils.env("TEST_TIME",default=10) #seconds


    nodes = collections.OrderedDict()
    nodeids = collections.OrderedDict()
    #redis cluster groups, each group is a list which contain the group node
    groups = []
    #map between node and (group, the number of the nodes in the group)
    groupmap = collections.OrderedDict()

    requestdata = {
        "min_processtime" : None,
        "max_processtime" : None,
        "total_processtime" : None,
        "total_requests" : 0,
        "get_requests" : 0,
        "set_requests" : 0,
        "errors": {
        },
        "groups": {
        }
    }


    @classmethod
    def setUpClass(cls):
        super(RedisClusterTestCase,cls).setUpClass()
        cls._cache = caches[cls.TEST_REDISCLUSTER_CACHE]
        if cls.REQUEST_INTERVAL :
            cls.REQUEST_INTERVAL = cls.REQUEST_INTERVAL / 1000
        cls._redis_client = cls._cache.redis_client
        nodes = cls._redis_client.cluster_nodes()
        nodeservers = [node for node in nodes.keys()]
        nodeservers.sort()
        for node in nodeservers:
            data = nodes[node]
            cls.nodeids[data["node_id"]] = node
            if "fail" in data["flags"]:
                cls.nodes[node] = {"id":data["node_id"],"is_master":None}
            elif "master" in data["flags"]:
                cls.nodes[node] = {"id":data["node_id"],"is_master":True, "slaves":[]}
            else:
                cls.nodes[node] = {"id":data["node_id"],"is_master":False, "master":None}

        print("============Reids Cluster Nodeids===================")
        print(json.dumps(cls.nodeids,indent=4))
        for node in nodeservers:
            data = nodes[node]
            if "master" in data["flags"] and "fail" not in data["flags"]:
                cls.groups.append([node])
                cls.groupmap[node] = (cls.groups[-1],len(cls.groups) - 1)


        for node in nodeservers:
            data = nodes[node]
            if "master" not in data["flags"] and "master_id" in data:
                group = cls.groupmap[cls.nodeids[data["master_id"]]]
                group[0].append(node)
                cls.groupmap[node] = group
                cls.nodes[cls.nodeids[data["master_id"]]]["slaves"].append(node)
                cls.nodes[node]["master"] = cls.nodeids[data["master_id"]]

        for group in cls.groups:
            group.sort()

        cls.groups.sort(key = lambda g:g[0])

        print("============Reids Cluster Nodes===================")
        print(json.dumps(cls.nodes,indent=4))
        print("============Reids Cluster Groups===================")
        print(json.dumps(cls.groups,indent=4))
        print("============Reids Cluster map between node and group===================")
        print(json.dumps(cls.groupmap,indent=4))

    def run_test(self,c_conn,group,groupdata,test_starttime,test_endtime):
        try:
            cls = self.__class__
            sleep_time = (test_starttime - timezone.localtime()).total_seconds()
            if sleep_time and sleep_time > 0:
                time.sleep(sleep_time)

            
            testingdata = {}
            getvalue=False
            while (timezone.localtime() < test_endtime) :
                starttime = timezone.localtime()
                key = groupdata[random.randrange(len(groupdata))]
                if key in testingdata:
                    getvalue = random.randrange(10) < 6
                else:
                    getvalue = False
                try:
                    if getvalue:
                        res = int(cls._redis_client.get(key))
                        if res != testingdata[key]:
                            raise DataMismatchException("{0} = {1}, expect {2}".format(key,res,testingdata[key]))
                    else:
                        val = testingdata.get(key,0) + 1
                        cls._redis_client.set(key,str(val),ex=86400)
                        testingdata[key] = val
                except DataMismatchException as ex:
                    cls.requestdata["errors"][ex.__class__.__name__] = cls.requestdata["errors"].get(ex.__class__.__name__,0) + 1
                except Exception as ex:
                    error = "{}({})".format(ex.__class__.__name__,traceback.format_exc())
                    print("Failed to {} {} from redis cluster group({}).error = {}".format("get" if getvalue else "set",key,group, error))
                    cls.requestdata["errors"][error] = cls.requestdata["errors"].get(error,0) + 1

                endtime = timezone.localtime()
                processtime = (endtime - starttime).total_seconds()
                if not cls.requestdata["min_processtime"] or cls.requestdata["min_processtime"] >  processtime:
                    cls.requestdata["min_processtime"] = processtime
        
                if not cls.requestdata["max_processtime"] or  cls.requestdata["max_processtime"] <  processtime:
                    cls.requestdata["max_processtime"] = processtime
        
                cls.requestdata["total_requests"] += 1
                if getvalue:
                    cls.requestdata["get_requests"] += 1
                else:
                    cls.requestdata["set_requests"] += 1
                if not cls.requestdata["total_processtime"]:
                    cls.requestdata["total_processtime"] = processtime
                else:
                    cls.requestdata["total_processtime"] += processtime
    
                if cls.REQUEST_INTERVAL > 0:
                    time.sleep(cls.REQUEST_INTERVAL)
    
            if c_conn:
                c_conn.send(cls.requestdata)
                c_conn.close()
        except Exception as ex:
            if c_conn:
                c_conn.send(ex)
                c_conn.close()
            else:
                raise

    def merge_requestdata(self,group,requestdata):
        cls = self.__class__
        group = ",".join(group)
        def _merge_requestdata(totaldata,requestdata):
            processtime = requestdata["min_processtime"]
            if not totaldata["min_processtime"] or totaldata["min_processtime"] >  processtime:
                totaldata["min_processtime"] = processtime
    
            processtime = requestdata["max_processtime"]
            if not totaldata["max_processtime"] or  totaldata["max_processtime"] <  processtime:
                totaldata["max_processtime"] = processtime
    
            totaldata["total_requests"] += requestdata["total_requests"]
            totaldata["get_requests"] += requestdata["get_requests"]
            totaldata["set_requests"] += requestdata["set_requests"]

            processtime = requestdata["total_processtime"]
            if not totaldata["total_processtime"]:
                totaldata["total_processtime"] = processtime
            else:
                totaldata["total_processtime"] += processtime

            totaldata["avg_processtime"] = totaldata["total_processtime"] / totaldata["total_requests"]
            for ex,counter in requestdata["errors"].items():
                totaldata["errors"][ex] = totaldata["errors"].get(ex,0) + counter

        if group not in cls.requestdata["groups"]:
            cls.requestdata["groups"][group] = {
                "min_processtime" : None,
                "max_processtime" : None,
                "total_processtime" : None,
                "total_requests" : 0,
                "get_requests" : 0,
                "set_requests" : 0,
                "errors": {
                }
            }

        _merge_requestdata(cls.requestdata["groups"][group],requestdata)

        _merge_requestdata(cls.requestdata,requestdata)

    def test_rediscluster(self):
        cls = self.__class__
        #prepare 1000 keys for each group
        keypattern = "testkey_{:010d}"
        index = 0

        groupsdata = [[]  for g in cls.groups]

        #prepare the data key for testing
        #generate the same amount of keys (cls.TEST_KEYS_PER_GROUP) for each redis cluster group
        counter = 0
        while True:
            index += 1
            key = keypattern.format(index)
            node = cls._redis_client.get_node_from_key(key)
            
            group = cls.groupmap[node.name]
            if len(groupsdata[group[1]]) < cls.TEST_KEYS_PER_GROUP:
                groupsdata[group[1]].append(key)

            if any(len(groupdata) < cls.TEST_KEYS_PER_GROUP for groupdata in groupsdata ):
                counter += 1
                if counter % cls.TEST_KEYS_PER_GROUP == 0:
                    print("Total {} keys generated.\n{}".format(counter,"\n".join( "{}={}".format(cls.groups[i],len(groupsdata[i])) for i in range(len(groupsdata)) )))
                continue
            else:
                print("Total {} keys generated.\n{}".format(counter,"\n".join( "{}={}".format(cls.groups[i],len(groupsdata[i])) for i in range(len(groupsdata)) )))
                break

        processes = []
        now = timezone.localtime()
        test_starttime = now + timedelta(seconds = 10)
        test_endtime = test_starttime + timedelta(seconds = self.TEST_TIME)
        keys_per_process = int(cls.TEST_KEYS_PER_GROUP / cls.TEST_PROCESSES_PER_GROUP)
        start_index = 0
        end_index = 0

        #start the process to test redis cluster
        #each key is operated by only one process
        for i in range(len(cls.groups)):
            for j in range(self.TEST_PROCESSES_PER_GROUP):
                start_index = keys_per_process * j
                if j == self.TEST_PROCESSES_PER_GROUP - 1:
                    end_index = cls.TEST_KEYS_PER_GROUP
                else:
                    end_index = start_index + keys_per_process
                p_conn, c_conn = Pipe()
                processes.append((cls.groups[i],p_conn,Process(target=self.run_test,args=(c_conn,cls.groups[i],groupsdata[i][start_index:end_index],test_starttime,test_endtime))))
    
        print("""Begin to run the unit test.
    Start Time: {0}
    End Time: {1}
    Request Interval: {2} milliseconds
    Total Processes: {3}
    Testing Groups: {4}({5})
    Processes Per Group: {6}
    Keys Per Group: {7}
    Keys Per Process: {8}""".format(
            utils.format_datetime(test_starttime),
            utils.format_datetime(test_endtime),
            cls.REQUEST_INTERVAL * 1000,
            len(processes),
            len(cls.groups),
            cls.groups,
            cls.TEST_PROCESSES_PER_GROUP,
            cls.TEST_KEYS_PER_GROUP,
            keys_per_process

        ))
        for group,p_conn,p in processes:
            p.start()
    
        exs = []
        for group,p_conn,p in processes:
            result = p_conn.recv()
            p.join()
            if isinstance(result,Exception):
                exs.append(result)
                continue
            
            self.merge_requestdata(group,result)



        print("==========Test Result=================")
        print(json.dumps(cls.requestdata,indent=4))
        
        if exs:
            print("===========Exceptions================")
            for ex in exs:
                print("{}:{}".format(ex.__class__.__name__,str(ex)))

        self.assertEqual(len(self.requestdata["errors"]) == 0 and not exs,True,msg="Some exceptions happened during testing")

