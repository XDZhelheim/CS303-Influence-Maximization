import multiprocessing as mp
import time
import sys
import argparse
import os
import random

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

    # def ISE_LT(self, seeds:list) -> int:
    #     self.marked=[False]*self.size
    #     for node in seeds:
    #         self.marked[node]=True
    #     activity_set=seeds.copy()
    #     thres=[]
    #     for i in range(self.size):
    #         ran=random.random()
    #         if ran==0 and i!=0:
    #             activity_set.append(i)
    #         thres.append(ran)
    #     count=len(activity_set)
    #     while activity_set:
    #         new_activity_set=[]
    #         neighbors=set()
    #         for node in activity_set:
    #             for edge in self.adj[node]:
    #                 if not self.marked[edge.v]:
    #                     neighbors.add(edge.v)
    #         for neighbor in neighbors:
    #             s=0
    #             for edge in self.inadj[neighbor]:
    #                 if self.marked[edge.v]:
    #                     s+=edge.w
    #             if s>=thres[neighbor]:
    #                 self.marked[neighbor]=True
    #                 new_activity_set.append(neighbor)
    #         count+=len(new_activity_set)
    #         activity_set=new_activity_set
    #     return count

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

class Edge:
    def __init__(self, u, v, w):
        self.u=u
        self.v=v
        self.w=w

def run_ISE(model:str, network:Graph, seeds:list):
    n=10000
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

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('-i', '--file_name', type=str, default='network.txt')
    parser.add_argument('-s', '--seed', type=str, default='seeds.txt')
    parser.add_argument('-m', '--model', type=str, default='IC')
    parser.add_argument('-t', '--time_limit', type=int, default=60)

    args=parser.parse_args()
    file_name=args.file_name
    seed=args.seed
    model=args.model
    time_limit=args.time_limit

    with open("./AI_Lab/Influence_Maximum/NetHEPT.txt") as f:
    # with open(file_name) as f:
        lines=f.readlines()
    first_line=lines[0].split(" ")
    network=Graph(int(first_line[0])+1)
    for i in range(1, len(lines)):
        line=lines[i].split(" ")
        network.add_directed_edge(int(line[0]), int(line[1]), float(line[2]))

    with open("./AI_Lab/Influence_Maximum/seeds.txt") as s:
    # with open(seed) as s:
        lines=s.readlines()
    seeds=[]
    for line in lines:
        seeds.append(int(line))

    print(run_ISE("IC", network, seeds))

    # result=0
    # pool = mp.Pool(core)
    # for i in range(core):
    #     result+=pool.apply_async(run_ISE, args=(model, network, seeds)).get()
    # pool.close()
    # pool.join()
    # result/=core
    # print(result)
    
    sys.stdout.flush()
    os._exit(0)
