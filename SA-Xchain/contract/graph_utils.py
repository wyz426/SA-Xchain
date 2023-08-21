#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Filename:graph_utils
# @Author:zekdot
# @Time: 2023/2/1 下午4:32
import json
from queue import Queue

from transaction.node import TYPE, get_node

# 对图的深拷贝
def copy_graph(starts: list):
    # 返回结果
    res = list()
    q = Queue()
    # 所有老节点
    nodes = list()
    # 所有新节点
    new_nodes = list()
    # id到节点的映射
    id2node = dict()
    id2new_node = dict()
    visited = set()
    # bfs算法进行一个搜索
    for start in starts:
        q.put(start)

    while not q.empty():
        cur = q.get()
        if cur.node_id in visited:
            continue
        visited.add(cur.node_id)
        new_node = cur.get_copy()
        new_nodes.append(new_node)
        nodes.append(cur)
        id2new_node[cur.node_id] = new_node
        id2node[cur.node_id] = cur
        for child in cur.children:
            q.put(child)

    for new_node in new_nodes:
        node = id2node[new_node.node_id]
        # 和父节点连接
        parent_ids = [n.node_id for n in node.parents]
        for parent_id in parent_ids:
            parent = id2new_node[parent_id]
            if parent not in new_node.parents:
                new_node.parents.add(parent)
            if new_node not in parent.children:
                parent.children.add(new_node)

    for new_node in new_nodes:
        if len(new_node.parents) == 0:
            res.append(new_node)
    return res

# 将图转化为json结构字符串
def graph_to_json_string(starts: list) -> str:
    # 分为两部分进行存储，一部分存储所有节点的信息，由唯一id进行映射，另一部分存储连接信息
    graph_map = dict()
    # id到节点映射
    graph_map['node'] = dict()
    # 连接列表
    graph_map['connect'] = list()
    q = Queue()
    for start in starts:
        q.put(start)
    # 防止重复访问
    visited = set()
    while not q.empty():
        cur = q.get()
        if cur.node_id in visited:
            continue
        visited.add(cur.node_id)
        # 存储节点
        graph_map['node'][cur.node_id] = cur.to_dict()
        # 存储连接信息，同时把子节点加入队列中
        for child in cur.children:
            graph_map['connect'].append((cur.node_id, child.node_id))
            q.put(child)
    # 将图转化为json字符串返回
    return json.dumps(graph_map, ensure_ascii=False)


# 由json字符串生成图
def json_string_to_graph(json_string: str) -> list:
    graph = json.loads(json_string)
    # print(json_string)
    # id到图节点映射
    node_id_to_node = dict()
    for node_id in graph['node']:
        node_id_to_node[node_id] = get_node(graph['node'][node_id])
    # print(node_id_to_node)
    # 进行连接
    for connect in graph['connect']:
        from_id = str(connect[0])
        to_id = str(connect[1])
        # 相互连接
        node_id_to_node[from_id].children.add(node_id_to_node[to_id])
        node_id_to_node[to_id].parents.add(node_id_to_node[from_id])
    # 返回所有入度为0的点作为start
    starts = list()
    for node_id in node_id_to_node:
        if len(node_id_to_node[node_id].parents) == 0:
            starts.append(node_id_to_node[node_id])
    return starts
