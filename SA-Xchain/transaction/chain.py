#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Filename:chain
# @Author:zekdot
# @Time: 2023/1/19 上午11:03
# 每条链上需要执行的操作
import logging.config
from queue import Queue

from contract.graph_utils import copy_graph
from transaction.exp_parse import parse_exp
from transaction.node import TYPE
from transaction.result import build_failed_result, build_finish_result, build_success_result
from transaction.test_graph import construct_loop_graph, construct_graph

logging.config.fileConfig(fname='logconfig.ini', disable_existing_loggers=False)
_logger = logging.getLogger('transactionLogger')
_temp_logger = logging.getLogger('tempLogger')


# 检测是否有环，以列表形式返回可能存在环的位置节点id
def find_loop(starts: list):
    # 获得一个图副本，然后拓扑排序
    copy_starts = copy_graph(starts)
    q = Queue()
    visited = set()
    # 获取全部节点列表
    for start in copy_starts:
        q.put(start)
    while True:
        # 假设有环
        loop = True
        q.put(None)
        while not q.empty():
            cur = q.get()
            # 如果已经处理完这层全部的节点了
            if not cur:
                # loop = False
                break
            # if cur.node_id in visited:
            #     continue
            # visited.add(cur.node_id)
            if len(cur.parents) == 0:
                loop = False
                for child in cur.children:
                    child.parents.discard(cur)
            for child in cur.children:
                # 继续检查
                q.put(child)

        # 全都处理完了，说明没有环
        if q.empty():
            return None

        # 有环返回环可能的位置
        if loop:
            break
    # 把所有可能有环的位置都进行返回
    res = list()
    while not q.empty():
        res.append(q.get().node_id)
    return res


class Chain:

    # 设置载参节点的值
    def set_params(self, kvpairs):
        # 直接加入到变量池中
        for k in kvpairs:
            self.var_pool[k] = kvpairs[k]

    # 设置链的初始化数据
    def set_init_data(self, kvpairs):
        for k in kvpairs:
            self.simulate_pool[k] = kvpairs[k]

    def set_write_read_speed(self, write_time, read_time):
        self.write_time = write_time
        self.read_time = read_time

    # 向模拟链中写入数据
    def write_data(self, key, value):
        key = key.strip()
        if value is not None:
            value = str(value).strip()
        # if '_expect_receive_time' in key:
        #     print('%s向链中写入%s-%s' % (self.desc, key, value))
        # TODO 需要完成真正的写入方法
        _logger.debug('向链中写入%s-%s' % (key, value))
        self.cur_time += self.write_time
        self.simulate_pool[key] = value

    # 读取模拟池中的数据
    def read_data(self, key):
        key = key.strip()
        # TODO 需要完成真正的读取方法
        value = self.simulate_pool.get(key)
        self.cur_time += self.read_time
        _logger.debug('从链中读取%s的值为%s' % (key, value))
        return value

    def __init__(self, chain_id: str, members: tuple, desc=''):
        self.cur_time = 0
        self.write_time = None
        self.read_time = None
        # 链id
        self.chain_id = chain_id
        # 全部成员
        self.members = members
        # 链描述
        self.desc = desc
        # 当前未结束的链
        self.working_member = None
        # 变量池
        self.var_pool = dict()
        # 变量备份池
        self.back_pool = dict()
        # 方法池
        self.func_pool = {'now()': lambda: 0}
        # 接收队列
        self.received_queue = None
        # 执行队列
        self.executing_queue = None
        # 当前已经执行过的点
        self.executed_nodes = None
        # 当前已经执行过的写入操作的key值
        self.written_keys = None

        # 设置模拟池
        self.simulate_pool = dict()

    def set_graph(self, starts: list):
        # 检测是否有环，有的话需要及时抛出异常
        loop_list = find_loop(starts)
        if loop_list:
            raise Exception('您的图中含有环！位于节点%s' % str(loop_list))
        # 赋值给运行图
        self.executing_queue = Queue()
        # 广播信息接收队列
        self.received_queue = Queue()
        # 重置未完成队列
        self.working_member = set(self.members)
        # 重制写节点列表
        self.written_keys = set()
        # 已经执行过的点
        self.executed_nodes = set()
        # 变量池
        self.var_pool = dict()
        # 变量备份池
        self.back_pool = dict()
        # 方法池
        self.func_pool = {'now()': lambda: 0}
        # 把初始节点都加入到执行队列中
        for start in starts:
            self.executing_queue.put(start)

    # 执行if语句并返回 执行完毕的变量，暂时无法执行的语句，需要广播的节点
    def _execute_if_node(self, node):
        condition = parse_exp(node.conditions, self.var_pool, self.func_pool)
        if condition:
            # 如果条件为真，就执行true_sub_node_list
            contain_nodes = node.true_sub_node_list
        else:
            # 否则执行false_sub_node_list
            contain_nodes = node.false_sub_node_list
        # 本次处理条件节点会返回的四个返回值
        new_vars = dict()
        back_vars = dict()
        broadcast_node_ids = list()
        unfinished_nodes = list()
        # 具体执行通过递归实现，获取的结果直接添加到最外层变量池缓存中即可
        for contain_node in contain_nodes:
            # 递归调用节点处理过程，并获得四个返回值
            sub_new_vars, sub_back_vars, sub_broadcast_node_ids, sub_unfinished_nodes = self._execute_node(contain_node)
            # 如果有执行失败的情况
            if sub_new_vars is None:
                # 直接返回失败
                return None, None, None, None
            # 将新产生的变量一同添加进返回新节点中
            for sub_new_var_key in sub_new_vars:
                # 后执行的节点已经会覆盖前一个执行的节点的变量
                new_vars[sub_new_var_key] = sub_new_vars[sub_new_var_key]
            for sub_back_var_key in sub_back_vars:
                back_vars[sub_back_var_key] = sub_back_vars[sub_back_var_key]
            broadcast_node_ids += sub_broadcast_node_ids
            unfinished_nodes += sub_unfinished_nodes
        # 返回该嵌套下处理完毕的所有值
        return new_vars, back_vars, broadcast_node_ids, unfinished_nodes

    # 执行一个节点，并返回新获得的变量
    def _execute_node(self, node):
        # 如果是参数节点，什么都不用做
        if node.node_type == TYPE.PARAM:
            # 参数类型节点直接返回空即可，因为变量会在启动过程的时候设置，不会产生新变量
            return {}, {}, [], []
        # 如果是读节点
        elif node.node_type == TYPE.READ:
            # 如果是无法执行的节点
            if node.chain_id != self.chain_id:
                # 如果是用于备份的数据或者是已经执行过的数据
                if node.need_backup or node.node_id in self.executed_nodes:
                    # 直接忽略即可
                    return {}, {}, [], []
                # 否则需要继续等待
                return {}, {}, [], [node]
            # 计算key的表达式
            read_key = parse_exp(node.key, self.var_pool, self.func_pool)
            # 读取返回值，如果失败的话需要进入回退状态
            try:
                read_value = self.read_data(read_key)
            except:
                return None, None, None, None
            if node.need_backup:
                # 如果是用于备份的数据，不需要传播给其他链，这里注意要返回的是key
                return {}, {read_key: read_value}, [], []
            else:
                # 否则需要将读取出来的值广播给其他节点
                return {node.var_name: read_value}, {}, [node.node_id], []
        elif node.node_type == TYPE.WRITE:
            # 只有在要操作的链节点上要进行实际的写入操作
            if node.chain_id == self.chain_id:
                # print(self.var_pool)
                # 计算key和value的表达式
                write_key = parse_exp(node.key, self.var_pool, self.func_pool)
                write_value = parse_exp(node.value, self.var_pool, self.func_pool)
                # 如果写入失败需要告知外界进入回退状态
                try:
                    # 调用API进行写入操作
                    self.write_data(write_key, write_value)
                except:
                    return None, None, None, None
                # 需要记录在写入节点列表中
                self.written_keys.add(write_key)
            # 写入操作不会引入新的变量，也不会有不能执行的问题等
            return {}, {}, [], []
        elif node.node_type == TYPE.VAR:
            var_key = node.var_name
            # 计算表达式值
            var_value = parse_exp(node.expression, self.var_pool, self.func_pool)
            # 变量操作会产生新的变量，但是不需要进行广播
            return {var_key: var_value}, {}, [], []
        elif node.node_type == TYPE.ROLLBACK:
            # 回滚状态直接通知外界即可
            return None, None, None, None
        elif node.node_type == TYPE.IF:
            new_vars, back_vars, broadcast_node_ids, unfinished_nodes = self._execute_if_node(node)
            # 如果子节点执行失败，需要通知外界
            if new_vars is None:
                return None, None, None, None
            # 需要将原本所有的子节点增加新的父节点，双向绑定
            for child in node.children:
                for sub_unfinished_node in unfinished_nodes:
                    child.parents.add(sub_unfinished_node)
                    sub_unfinished_node.children.add(child)
            return new_vars, back_vars, broadcast_node_ids, unfinished_nodes
        else:
            return None, None, None, None

    # 进行回退，撤销写节点的操作
    def _fall_back(self):
        # 对每个执行过的写节点进行回退
        for written_key in self.written_keys:
            self.write_data(written_key, self.back_pool[written_key])
            _logger.debug("回退写入%s-%s" % (written_key, self.back_pool[written_key]))

    def execute_once(self):
        # 返回结果
        # 首先遍历接收队列中的每一个元素进行执行
        while not self.received_queue.empty():
            # 获取结果
            result = self.received_queue.get()
            # 如果是完成通知
            if result.finish:
                # 将该成员从工作成员集合中移除
                self.working_member.discard(result.chain_id)
                continue
            # 如果是回退通知
            if not result.success:
                # 进入回退阶段
                self._fall_back()
                # 将该成员加入到结束成员列表中，同时标识自己已经执行完毕
                self.working_member.discard(result.chain_id)
                self.working_member.discard(self.chain_id)
                # 返回回退数据包
                return [build_failed_result(self.chain_id)]
            # 标记对应点已经执行完成
            for node_id in result.node_ids:
                self.executed_nodes.add(node_id)
            # 将变量加到变量池中
            for key in result.kv_pairs:
                self.var_pool[key] = result.kv_pairs[key]

        # 没有更多节点可以执行了
        if self.executing_queue.empty():
            # 标记自己完成
            self.working_member.discard(self.chain_id)
            # 将完成的信息广播给其他的链
            return [build_finish_result(self.chain_id)]
        # 用于标记执行完成
        # self.executing_queue.put(None)
        # 保存本轮执行仍无法执行的节点
        batch_unfinished_nodes = list()
        # 要广播的变量列表
        batch_new_vars = dict()
        # 要广播的节点列表
        batch_broadcast_node_ids = list()
        # 执行一波队列中的节点
        while not self.executing_queue.empty():
            node = self.executing_queue.get()
            # 本次执行结束
            # if node is None:
            #     break
            # 执行该节点获取结果，获取执行得到的变量
            new_vars, back_vars, broadcast_node_ids, unfinished_nodes = self._execute_node(node)
            # 返回None说明运行失败，可能是读写接口的问题，直接返回失败信息 !!这里不能用not execute_res，因为not {}也是True
            if new_vars is None:
                # 返回回退数据包，同时进入回退阶段
                self._fall_back()
                self.working_member.discard(self.chain_id)
                return [build_failed_result(self.chain_id)]
            # 将所有广播信息增加到本轮次广播列表中
            batch_broadcast_node_ids += broadcast_node_ids
            # 变量需要添加到自己的变量池中
            for key in new_vars:
                self.var_pool[key] = new_vars[key]
                batch_new_vars[key] = new_vars[key]
            # 将备份变量添加到备份变量池中
            for key in back_vars:
                self.back_pool[key] = back_vars[key]
            # 把所有没有完成的节点继续添加批次未完成节点列表
            for unfinished_node in unfinished_nodes:
                batch_unfinished_nodes.append(unfinished_node)
            # 如果本节点也在无法执行的节点列表中，直接跳过
            if node in unfinished_nodes:
                continue
            if self.chain_id == '0x0001':
                _temp_logger.info('成功执行节点%s' % node.node_id)
            # 遍历该节点的所有子节点
            for child in node.children:
                # 删除子节点的入度
                child.parents.discard(node)
                # 如果子节点的入度为0
                if len(child.parents) == 0:
                    # 添加到执行队列中
                    self.executing_queue.put(child)
        # 未完成节点加入到队列中
        for unfinished_node in batch_unfinished_nodes:
            self.executing_queue.put(unfinished_node)
        # 将执行成功的节点连同新产生的变量一起添加到广播中
        return [build_success_result(self.chain_id, batch_broadcast_node_ids, batch_new_vars)]
        # return packages

    def receive_result_from(self, results):
        # 结果需要直接加入到队列中去进行执行
        for result in results:
            self.received_queue.put(result)

    def is_finish(self):
        # 判断所有参与节点是否都已经完成
        return len(self.working_member) == 0


if __name__ == '__main__':
    # pass
    chain = Chain('0xfdsa', ('fdsaf', 'fdsaf'), '测试')
    loop_start = construct_loop_graph()
    chain.set_graph(loop_start)
    # print(find_loop(loop_start))
    starts = construct_graph()
    chain.set_graph(starts)
    # print(find_loop(starts))
    # print('Hello World')
    # chain = Chain('dfsf')
    # chain.var_pool = {'as': 4, 'df': 3, 'xy': '鲱鱼', 'now()': lambda: 123}
    # print(chain.parse_exp('($as+$df)/2*$df+$now()'))
    # print(chain.parse_exp('$as<5 and $df>4 or $xy=="鲱鱼"'))
    # print(chain.parse_exp('鲱鱼'))
