import time
import sys
import argparse
import os
import random
import math
import multiprocessing as mp

core = 8

class Graph:
    def __init__(self, size):
        self.size=size
        self.adj=[[] for i in range(size)]
        self.inadj=[[] for i in range(size)]
        self.marked=None
    
    def add_directed_edge(self, u, v, w):
        self.adj[u].append(Edge(u, v, w))
        self.inadj[v].append(Edge(v, u, w))

    def ISE_IC(self, seeds:list) -> int:
        self.marked=[False]*self.size
        for node in seeds:
            self.marked[node]=True
        activity_set=seeds.copy()
        count=len(activity_set)
        while activity_set:
            new_activity_set=[]
            for node in activity_set:
                for edge in self.adj[node]:
                    if self.marked[edge.v]:
                        continue
                    p=random.random()
                    if p<=edge.w:
                        self.marked[edge.v]=True
                        new_activity_set.append(edge.v)
            count+=len(new_activity_set)
            activity_set=new_activity_set
        return count

    def ISE_LT(self, seeds:list) -> int:
        self.marked=[False]*self.size
        for node in seeds:
            self.marked[node]=True
        activity_set=seeds.copy()
        thres=[]
        acti=[0]*network.size
        for i in range(self.size):
            ran=random.random()
            if ran==0 and i!=0:
                activity_set.append(i)
            thres.append(ran)
        count=len(activity_set)
        while activity_set:
            new_activity_set=[]
            for node in activity_set:
                for edge in self.adj[node]:
                    if not self.marked[edge.v]:
                        acti[edge.v]+=edge.w
                        if acti[edge.v]>=thres[edge.v]:
                            self.marked[edge.v]=True
                            new_activity_set.append(edge.v)
            count+=len(new_activity_set)
            activity_set=new_activity_set
        return count

    def random_RR_IC(self, v) -> list:
        self.marked=[False]*self.size
        self.marked[v]=True
        activity_set=[v]
        nodes=[v]
        while activity_set:
            new_activity_set=[]
            for node in activity_set:
                for edge in self.inadj[node]:
                    if self.marked[edge.v]:
                        continue
                    p=random.random()
                    if p<=edge.w:
                        self.marked[edge.v]=True
                        new_activity_set.append(edge.v)
                        nodes.append(edge.v)
            activity_set=new_activity_set
        return nodes

    def random_RR_LT(self, v) -> list:
        self.marked=[False]*self.size
        self.marked[v]=True
        activity_node=v
        nodes=[v]
        while activity_node:
            new_activity_node=0
            neighbors=[]
            for edge in self.inadj[activity_node]:
                neighbors.append(edge.v)
            if not neighbors:
                break
            new_activity_node=random.choice(neighbors)
            if not self.marked[new_activity_node]:
                self.marked[new_activity_node]=True
                nodes.append(new_activity_node)
            else:
                new_activity_node=0
            activity_node=new_activity_node
        return nodes

class Edge:
    def __init__(self, u, v, w):
        self.u=u
        self.v=v
        self.w=w

def run_ISE(model:str, network:Graph, seeds:list):
    n=100
    count=0
    result=0
    start=time.time()
    while count<n:
        result+=network.ISE_IC(seeds) if model=="IC" else network.ISE_LT(seeds)
        count+=1
        t=time.time()
        if (t-start>110):
            break
    result/=count
    return result

def logCnk(n, k):
    s=0
    for i in range(n-k+1, n+1):
        s+=math.log(i)
    for i in range(1, k+1):
        s-=math.log(i)
    return s

def random_RR(model:str, network:Graph, v):
    return network.random_RR_IC(v) if model=="IC" else network.random_RR_LT(v)

def random_RR_mp(model, network, length):
    result=[]
    for i in range(length):
        result.append(random_RR(model, network, random.randint(1, network.size-1)))
    return result

# def node_selection(network:Graph, R:list, k:int):
#     Sk=[]
#     node_deg=[0]*network.size
#     node_RR=[[] for i in range(network.size)]
#     count=0
#     for i in range(0, len(R)):
#         RR=R[i]
#         for node in RR:
#             node_deg[node]+=1
#             node_RR[node].append(i)
#     for i in range(k):
#         maxnode=np.argmax(np.array(node_deg))
#         Sk.append(maxnode)
#         count+=len(node_RR[maxnode])
#         temp=node_RR[maxnode].copy()
#         for j in temp:
#             RR=R[j]
#             for node in RR:
#                 node_deg[node]-=1
#                 node_RR[node].remove(j)
#     return Sk, count/len(R)

def node_selection(network:Graph, R:list, k:int):
    Sk=[]
    in_RRs=[[] for i in range(network.size)]
    count=0
    for RR in R:
        for node in RR:
            in_RRs[node].append(RR)
    for i in range(k):
        maxnode=1
        for node in range(1, network.size):
            if len(in_RRs[node])>len(in_RRs[maxnode]):
                maxnode=node
        Sk.append(maxnode)
        count+=len(in_RRs[maxnode])
        temp=in_RRs[maxnode].copy()
        for RR in temp:
            for node in RR:
                in_RRs[node].remove(RR)
    return Sk, count/len(R)

def sampling(model:str, network:Graph, k:int, ep, l) -> list:
    R=[]
    LB=1
    n=network.size-1
    ep_prime=ep*math.sqrt(2)
    for i in range(1, int(math.log2(n))):
        x=n/pow(2, i)
        lambda_prime=((2+2*ep_prime/3)*(logCnk(n, k)+l*math.log(n)+math.log(math.log2(n)))*n)/pow(ep_prime, 2)
        theta=lambda_prime/x

        # while len(R)<=theta:
        #     v=random.randint(1, n)
        #     R.append(random_RR(model, network, v))

        pool = mp.Pool(core)
        for i in range(core):
            R+=pool.apply_async(random_RR_mp, args=(model, network, int((theta-len(R))/core))).get()

        S, FR=node_selection(network, R, k)
        if n*FR>=(1+ep_prime)*x:
            LB=n*FR/(1+ep_prime)
            break
    a=math.sqrt(l*math.log(n)+math.log(2))
    b=math.sqrt((1-1/math.e)*(logCnk(n, k)+l*math.log(n)+math.log(2)))
    lambda_star=2*n*pow(((1-1/math.e)*a+b), 2)*pow(ep, -2)
    theta=lambda_star/LB

    # while len(R)<=theta:
    #     v=random.randint(1, n)
    #     R.append(random_RR(model, network, v))

    for i in range(core):
        R+=pool.apply_async(random_RR_mp, args=(model, network, int((theta-len(R))/core))).get()
    pool.close()
    pool.join()

    return R

def IMM(model:str, network:Graph, k:int, ep, l):
    l=l*(1+math.log(2)/math.log(network.size-1))

    s=time.time()
    R=sampling(model, network, k, ep, l)
    e=time.time()
    # print("Sampling: "+str(e-s))

    s=time.time()
    Sk, FR=node_selection(network, R, k)
    e=time.time()
    # print("NodeSelection: "+str(e-s))

    return Sk

# def sampling_timelimit(model, network, time_limit):
#     R=[]
#     start=time.time()
#     while True:
#         v=random.randint(1, network.size-1)
#         R.append(random_RR(model, network, v))
#         end=time.time()
#         if (end-start>10):
#             break
#     end=time.time()
#     print("Time:"+str(end-start))
#     return R

# def IMM_timelimit(model, network, k, time_limit):
#     R=sampling_timelimit(model, network, time_limit)
#     start=time.time()
#     Sk, FR=node_selection(network, R, k)
#     end=time.time()
#     print("Time:"+str(end-start))
#     return Sk

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('-i', '--file_name', type=str, default='network.txt')
    parser.add_argument('-k', '--seedCount', type=int, default=5)
    parser.add_argument('-m', '--model', type=str, default='IC')
    parser.add_argument('-t', '--time_limit', type=int, default=60)

    args=parser.parse_args()
    file_name=args.file_name
    seed_count=args.seedCount
    model=args.model
    time_limit=args.time_limit

    # with open("./AI_Lab/Influence_Maximum/network.txt") as f:
    with open(file_name) as f:
        lines=f.readlines()
    first_line=lines[0].split(" ")
    network=Graph(int(first_line[0])+1)
    for i in range(1, len(lines)):
        line=lines[i].split(" ")
        network.add_directed_edge(int(line[0]), int(line[1]), float(line[2]))

    # 50: e=0.06/0.075
    result=IMM(model, network, seed_count, 0.1, 1)
    # result=IMM_timelimit(model, network, seed_count, time_limit)
    for value in result:
        print(value)

    # print(run_ISE(model, network, list(result)))

    sys.stdout.flush()
    os._exit(0)
