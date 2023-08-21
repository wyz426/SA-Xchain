#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Filename:result
# @Author:zekdot
# @Time: 2023/1/19 上午11:42

class Result:

    # 结果不需要考虑是否是写入，因为写入操作是一个终端节点，不会有人等待它的
    def __init__(self):
        # 是否是最后一条
        self.finish = False
        # 是否执行成功
        self.success = False
        # 链id
        self.chain_id = ''
        # 提示这些信息由哪些节点完成而产生的
        self.node_ids = []
        # 键值对
        self.kv_pairs = dict()


# 返回某个链的失败结果
def build_failed_result(chain_id):
    result = Result()
    result.success = False
    result.chain_id = chain_id
    return result


# 返回某个链的某个节点成功运行的结果
def build_success_result(chain_id: str, node_ids: list, nkv_pairs: dict):
    result = Result()
    result.success = True
    result.chain_id = chain_id
    result.node_ids = node_ids
    for nk in nkv_pairs:
        result.kv_pairs[nk] = nkv_pairs[nk]
    return result


# 返回某个链全部节点成功运行的结果
def build_finish_result(chain_id):
    result = Result()
    result.finish = True
    result.success = True
    result.chain_id = chain_id
    return result


if __name__ == '__main__':
    print('Hello World')
