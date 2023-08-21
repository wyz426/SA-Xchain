#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Filename:test_graph
# @Author:zekdot
# @Time: 2023/3/26 下午3:19
# 测试图
from transaction.node import *

# 这里假设有三条链，以下是三条链的链id
fisher_chain_id = '0x1234'  # 渔业联盟链
factory_chain_id = '0x2345'   # 加工厂联盟链
merchant_chain_id = '0x4567'     # 商家联盟链


def construct_graph():
    N1 = Param(1, 'fish_id')  # 鱼批次输入
    N2 = Param(2, 'merchant_id')  # 商家id获取
    N3 = Param(3, 'fisher_id')  # 渔公司id获取
    N4 = Param(4, 'factory_id')  # 加工厂id获取
    N5 = Read(5, merchant_chain_id, '$fish_id:expect_receive_time', 'a', True)  # 预期收货时间
    N6 = Read(6, factory_chain_id, '$fish_id:process_method', 'a', True)  # 加工方式
    N7 = Read(7, fisher_chain_id, '$fish_id:temperature', 'a')  # 存储温度
    N8 = Read(8, fisher_chain_id, '$fish_id:fish_type', 'a')  # 鱼种类
    N9 = Read(9, merchant_chain_id, '$fish_id:factory', True)  # 商家链记录的负责加工的加工厂
    N10 = Read(10, fisher_chain_id, '$fish_id:factory', True)  # 渔业公司记录的负责加工的加工厂
    N11 = Read(11, factory_chain_id, '$fish_id:fisher', True)  # 加工厂记录的渔业公司
    N12 = Read(12, factory_chain_id, '$fish_id:merchant', True)  # 加工厂链中记录的商家信息
    N13 = Variable(13, 'temperature', '$($fish_id:temperature)')  # 中间变量温度
    N14 = Variable(14, 'fish_type', '$($fish_id:fish_type)')  # 中间变量鱼种类
    N15 = Write(15, factory_chain_id, '$fish_id:process_method', '$process_method')  # 写入加工方式到加工厂链
    N16 = If(16)
    N17 = If(17)
    N18 = If(18)
    N19 = If(19)
    N20 = Write(20, fisher_chain_id, '$fish_id:factory', '$factory_id')  # 渔业链存储的加工厂信息
    N21 = Write(21, factory_chain_id, '$fish_id:fisher', '$fisher_id')
    N22 = Write(22, factory_chain_id, '$fish_id:merchant', '$merchant_id')  # 加工厂链写入的商家信息
    N23 = Read(23, factory_chain_id, '$fish_id:merchant', True)  # 加工厂链中记录的商家信息
    N24 = Write(24, merchant_chain_id, '$fish_id:factory', '$factory_id')  # 商家链上的加工厂信息
    N25 = Read(25, factory_chain_id, '$fish_id:expect_send_time', True)  # 预期发货时间
    N26 = Variable(26, 'expect_send_time', '$cost_time * 24 * 3600 + $now()')  # 预期提交时间变量
    N27 = Write(27, merchant_chain_id, '$fish_id:expect_receive_time', '$expect_send_time')  # 商家预期收货时间
    N28 = Write(28, factory_chain_id, '$fish_id:expect_send_time', '$expect_send_time')  # 加工厂预期提交时间

    # 节点1
    N1.children = [N5, N6, N7, N8, N9, N25, N10, N11, N12]

    # 节点2
    N2.children = [N20, N24]

    # 节点3
    N3.children = [N21]

    # 节点4
    N4.children = [N22]

    # 节点5
    N5.parents = [N1]
    N5.children = [N27]

    # 节点6
    N6.parents = [N1]
    N6.children = [N15]

    # 节点7
    N7.parents = [N1]
    N7.children = [N13]

    # 节点8
    N8.parents = [N1]
    N8.children = [N14]

    # 节点9
    N9.parents = [N1]
    N9.children = [N24]

    # 节点10
    N10.parents = [N1]
    N10.children = [N20]

    # 节点11
    N11.parents = [N1]
    N11.children = [N21]

    # 节点12
    N12.parents = [N1]
    N12.children = [N22]

    # 节点13
    N13.parents = [N7]
    N13.children = [N16, N17, N18, N19]

    # 节点14
    N14.parents = [N8]
    N14.children = [N16]

    # 节点15
    N15.parents = [N6, N16, N17, N18]
    N15.children = []

    # 节点16
    # 需要处理内部节点等
    N16.parents = [N13, N14]
    N16.children = [N15, N26]
    N16.conditions = '($temperature < 10 and $temperature >= 5) or $fish_type == 456'
    N16.contains_nodes = [Variable(0, 'cost_time', 5), Variable(0, 'process_method', 1)]

    # 节点17
    # 需要处理内部节点等
    N17.parents = [N13]
    N17.children = [N26, N15]
    N17.conditions = '$temperature < 0'
    N17.contains_nodes = [Variable(0, 'cost_time', 1), Variable(0, 'process_method', 2)]

    # 节点18
    # 需要处理内部节点等
    N18.parents = [N13]
    N18.children = [N15, N26]
    N18.conditions = '$temperature < 5 and $temperature >= 0'
    N18.contains_nodes = [Variable(0, 'cost_time', '1'), Variable(0, 'process_method', 3)]

    # 节点19
    # 需要处理内部节点等
    N19.parents = [N13]
    N19.children = []
    N19.conditions = '$temperature >= 10'
    N19.contains_nodes = [Rollback(0)]

    # 节点20
    N20.parents = [N2, N10]
    N20.children = []

    # 节点21
    N21.parents = [N3, N11]
    N21.children = []

    # 节点22
    N22.parents = [N4, N12]
    N22.children = []

    # 节点23
    N23.parents = []
    N23.children = [N26]

    # 节点24
    N24.parents = [N2, N9]
    N24.children = []

    # 节点25
    N25.parents = [N1]
    N25.children = [N28]

    # 节点26
    N26.parents = [N16, N17, N18, N23]
    N26.children = [N27, N28]

    # 节点27
    N27.parents = [N5, N26]
    N27.children = []

    # 节点28
    N28.parents = [N25, N26]
    N28.children = []
    return [N1, N2, N3, N4, N23]


# 构造有环图
def construct_loop_graph():
    N0 = Param(1, 'test')
    N1 = Read(2, fisher_chain_id, 'storage_amount','a')
    N2 = Read(3, 'price_department', 'price','a')
    N3 = Read(4, 'forecast_group', 'expected_sell_amount', 'a')
    N0.children = [N1]
    N1.children = [N2]
    N1.parents = [N0, N3]
    N2.children = [N3]
    N2.parents = [N1]
    N3.children = [N1]
    N3.parents = [N2]
    return [N0]


if __name__ == '__main__':
    print('Hello World');
