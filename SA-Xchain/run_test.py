#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Filename:run_test
# @Author:zekdot
# @Time: 2023/3/28 下午9:26
import json
import logging.config

from contract.compile_exception import CompileException
from contract.contract_parser import parse_code
from contract.graph_utils import graph_to_json_string, json_string_to_graph
from transaction.chain import Chain

logging.config.fileConfig(fname='logconfig.ini', disable_existing_loggers=False)
_logger = logging.getLogger('testLogger')


class Result:

    def __init__(self, result, count, all, compile_info, cases):
        self.result = result
        self.count = count
        self.all = all
        self.compile = compile_info
        self.cases = cases

    def to_dict(self):
        return {
            'result': self.result,
            'count': self.count,
            'all': self.all,
            'compile_info': self.compile,
            'cases': [case.to_dict() for case in self.cases] if self.cases is not None else None
        }


class Case:

    def __init__(self, success: bool, output: list):
        self.success = success
        self.output = output

    def to_dict(self):
        return {
            "success": self.success,
            "output": self.output
        }


# 返回格式 {result: 0, count: 0, all: 6, cases: {}, compile_info: ""}
# result        运行结果 0 通过全部用例   1 通过部分用例  2 编译失败
# count         当前通过用例个数
# all           总用例个数
# compile_info  编译信息，如果编译没有通过，行数:信息
# cases      用例的执行情况
# 如果是其他情况，每行都是一个字符串
def run_test(usercode: str, code: str, data: dict):
    # _logger.info('用户%s提交脚本内容为%s' % (usercode, code))
    # _logger.info('对用户%s的脚本进行编译' % usercode)
    try:
        starts = parse_code(code)
    except CompileException as e:
        e.info.insert(0, e.line)
        return Result(2, 0, 0, e.info, None)
    json1 = graph_to_json_string(starts)
    # _logger.info('用户%s图输出为%s' % (usercode, json1))
    print(json1)

    # print(data)
    _logger.info('用户%s初始化各链信息' % usercode)
    # 初始化链的信息
    chain_data = data['chains']
    chain_ids = tuple([chain_data[k]['chain_id'] for k in chain_data])
    chains = dict()
    for chain_name in chain_data:
        # 初始化所有链
        chains[chain_name] = Chain(chain_data[chain_name]['chain_id'],
                                   chain_ids,
                                   chain_data[chain_name]['desc'])
        # 设置读写花费时间
        chains[chain_name].set_write_read_speed(chain_data[chain_name]['write_time'],
                                                chain_data[chain_name]['read_time'])

    _logger.info('用户%s设置各链的初始数据' % usercode)
    for chain_name in chain_data:
        # 初始化所有链
        chains[chain_name].set_init_data(chain_data[chain_name]['data'])
        _logger.info("用户%s在%s初始数据为%s" % (usercode, chain_data[chain_name]['desc'],
                                                 str(chains[chain_name].simulate_pool)))

    _logger.info('用户%s开始进行测试' % usercode)
    test_data = data['tests']
    # 通过用例个数
    count = 0
    # 用例详情
    cases = list()
    # 总用例个数
    all = len(test_data)
    for i, test in enumerate(test_data):
        # 设置到返回值中

        # 用例输出
        output = list()

        output.append(''.join(['-' for i in range(50)]))
        _logger.info("用户%s运行测试%d-%s" % (usercode, i, test['desc']))
        _logger.info('用户%s设置图' % usercode)
        for chain_name in chains:
            # 设置执行时需要的参数
            chains[chain_name].set_graph(json_string_to_graph(json1))
        _logger.info('用户%s设置运行参数' % usercode)
        params = dict()
        output.append('用例参数为：')
        for param_key in test['input']:
            params[param_key] = test['input'][param_key]
            output.append('%s=%s' % (param_key, test['input'][param_key]))
        for chain_name in chains:
            # 设置执行时需要的参数
            chains[chain_name].set_params(params)
            # 初始化当前时间
            chains[chain_name].cur_time = 0


        execute_times=0
        # 当三条中任意一条没有执行完成时
        while execute_times < 60000:
            for chain_name in chains:
                cur_chain = chains[chain_name]
                # 执行并广播
                if not cur_chain.is_finish():
                    results = cur_chain.execute_once()
                    # 给其他链广播一下
                    if len(results) > 0:
                        for other_chain in chains:
                            if other_chain != chain_name:
                                chains[other_chain].receive_result_from(results)
            # 检测是否运行结束
            flag = True
            # 如果全部链执行结束，退出循环
            for chain_name in chains:
                # 设置执行时需要的参数
                if not chains[chain_name].is_finish():
                    flag = False
                    break
            if flag:
                break
            execute_times += 1
        print('一共执行了%s次' % execute_times)
        _logger.info('一共执行了%s次' % execute_times)
        if execute_times >= 60000:
            return Result(2, 0, 0, [0, "请检查是否写错了write或read语句中的链id"], None)
        output.append('结果为:')
        _logger.info('用户%s和预期进行比较' % usercode)
        expect = test['expect']
        all_right = True
        for chain_name in chains:
            cur_chain = chains[chain_name]
            # _logger.info('用户%s查看%s' % (cur_chain.desc, usercode))

            for k in expect[chain_name]:

                wanted = expect[chain_name][k]
                actual = cur_chain.simulate_pool.get(k)
                if wanted != actual:
                    all_right = False
                    output.append('%s上键%s的预期和结果不相符，预期为%s，结果为%s' %
                                    (cur_chain.desc, str(k), str(wanted), str(actual)))
                    # print(cur_chain.simulate_pool)
                    _logger.warning('用户%s在%s上键%s的预期和结果不相符，预期为%s，结果为%s' %
                                    (usercode, cur_chain.desc, str(k), str(wanted), str(actual)))
            _logger.info('%s链(读：%s, 写：%s)当前时间为%s' % (cur_chain.desc, cur_chain.read_time,
                                                             cur_chain.write_time, cur_chain.cur_time))
        if all_right:
            count += 1
            output.append('测试均通过')
            _logger.info('用户%s测试均通过' % usercode)
        output.append(''.join(['-' for i in range(50)]))
        output.insert(0, '运行测试%d，结果为%s' % (i + 1, '成功' if all_right else '失败'))
        cases.append(Case(all_right, output))
    return Result(0 if all == count else 1, count, all, None, cases)
