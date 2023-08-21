#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Filename:node_define
# @Author:zekdot
# @Time: 2023/1/13 上午10:54
# 通用节点定义


class TYPE:
    PARAM = 0   # 参数传入
    READ = 1  # 读数据
    WRITE = 2  # 写数据
    VAR = 3  # 中间变量
    IF = 4 # 条件语句
    ROLLBACK = 5  # 回滚


class Node:
    node_id = '0'  # 节点id
    node_type = None  # 节点类型
    parents = None  # 父节点集合
    children = None  # 子节点集合


# 参数节点
class Param(Node):
    node_type = TYPE.PARAM
    name = ''

    def __init__(self, node_id, name):
        self.node_id = node_id
        self.name = name
        self.parents = set()  # 父节点集合
        self.children = set()  # 子节点集合

    def get_copy(self):
        return Param(self.node_id, self.name)

    def to_dict(self):
        return {'node_type': TYPE.PARAM, 'node_id': self.node_id, 'name': self.name}


# 读取节点
class Read(Node):
    node_type = TYPE.READ
    chain_id = ''  # 要读取的链id
    key = ''  # 要读取的数据键
    var_name = '' # 要生成的变量名
    need_backup = False    # 是否需要副本

    def __init__(self, node_id, chain_id, key, var_name, need_backup=False):
        self.node_id = node_id
        self.chain_id = chain_id
        self.key = key
        self.var_name = var_name
        self.parents = set()  # 父节点集合
        self.children = set()  # 子节点集合
        self.need_backup = need_backup

    def get_copy(self):
        return Read(self.node_id, self.chain_id, self.key, self.var_name, self.need_backup)

    def to_dict(self):
        return {'node_type': TYPE.READ, 'node_id': self.node_id, 'chain_id': self.chain_id,
                'key': self.key, 'var_name': self.var_name, 'need_backup': self.need_backup}


# 写入节点
class Write(Node):
    node_type = TYPE.WRITE
    chain_id = ''  # 要写入的链id
    key = ''  # 要写入的key
    executed = False    # 是否已经执行过
    value = ''  # 要写入的value

    def __init__(self, node_id, chain_id, key, value, executed = False):
        self.node_id = node_id
        self.chain_id = chain_id
        self.key = key
        self.value = value
        self.parents = set()  # 父节点集合
        self.children = set()  # 子节点集合
        self.executed = executed

    def get_copy(self):
        return Write(self.node_id, self.chain_id, self.key, self.value, self.executed)

    def to_dict(self):
        return {'node_type': TYPE.WRITE, 'node_id': self.node_id, 'chain_id': self.chain_id,
                'key': self.key, 'value': self.value}


# 中间变量节点
class Variable(Node):
    node_type = TYPE.VAR
    var_name = ''  # 变量名
    expression = ''  # 变量值

    def __init__(self, node_id, var_name, expression):
        self.node_id = node_id
        self.var_name = var_name
        self.expression = expression
        self.parents = set()  # 父节点集合
        self.children = set()  # 子节点集合

    def get_copy(self):
        return Variable(self.node_id, self.var_name, self.expression)

    def to_dict(self):
        return {'node_type': TYPE.VAR, 'node_id': self.node_id, 'var_name': self.var_name, 'expression': self.expression}


# 条件节点
class If(Node):
    node_type = TYPE.IF
    conditions = ''  # 需要满足的条件
    # 条件为真时要执行的子节点
    true_sub_node_list = []
    # 条件为假时要执行的子节点
    false_sub_node_list = []

    def __init__(self, node_id):
        self.node_id = node_id
        self.true_sub_node_list = list()
        self.false_sub_node_list = list()
        self.parents = set()  # 父节点集合
        self.children = set()  # 子节点集合

    def get_copy(self):
        new_node = If(self.node_id)
        new_node.conditions = self.conditions
        for contain_node in self.true_sub_node_list:
            new_node.true_sub_node_list.append(contain_node.get_copy())
        for contain_node in self.false_sub_node_list:
            new_node.false_sub_node_list.append(contain_node.get_copy())
        return new_node

    def to_dict(self):
        res = dict()
        res['node_type'] = TYPE.IF
        res['node_id'] = self.node_id
        res['conditions'] = self.conditions
        res['true_sub_node_list'] = list()
        res['false_sub_node_list'] = list()
        for true_sub_node in self.true_sub_node_list:
            res['true_sub_node_list'].append(true_sub_node.to_dict())
        for false_sub_node in self.false_sub_node_list:
            res['false_sub_node_list'].append(false_sub_node.to_dict())
        return res


# 回滚节点
class Rollback(Node):
    node_type = TYPE.ROLLBACK

    def __init__(self, node_id):
        self.node_id = node_id
        self.parents = set()  # 父节点集合
        self.children = set()  # 子节点集合

    def get_copy(self):
        return Rollback(self.node_id)

    def to_dict(self):
        return {'node_type': TYPE.ROLLBACK, 'node_id': self.node_id}


def get_node(node_dict: dict):
    if node_dict['node_type'] == TYPE.PARAM:
        return Param(node_dict['node_id'], node_dict['name'])
    elif node_dict['node_type'] == TYPE.READ:
        return Read(node_dict['node_id'], node_dict['chain_id'], node_dict['key'],
                    node_dict['var_name'], node_dict['need_backup'])
    elif node_dict['node_type'] == TYPE.WRITE:
        return Write(node_dict['node_id'], node_dict['chain_id'], node_dict['key']
                     , node_dict['value'])
    elif node_dict['node_type'] == TYPE.VAR:
        return Variable(node_dict['node_id'], node_dict['var_name'], node_dict['expression'])
    elif node_dict['node_type'] == TYPE.IF:
        new_node = If(node_dict['node_id'])
        new_node.conditions = node_dict['conditions']
        new_node.true_sub_node_list = list()
        new_node.false_sub_node_list = list()
        for true_sub_node in node_dict['true_sub_node_list']:
            new_node.true_sub_node_list.append(get_node(true_sub_node))
        for false_sub_node in node_dict['false_sub_node_list']:
            new_node.false_sub_node_list.append(get_node(false_sub_node))
        return new_node
    elif node_dict['node_type'] == TYPE.ROLLBACK:
        return Rollback(node_dict['node_id'])
    return None
