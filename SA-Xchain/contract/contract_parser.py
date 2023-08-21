#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Filename:contract_parser
# @Author:zekdot
# @Time: 2023/2/4 下午3:38
# 对合约进行解析
import re
import logging.config

from contract.compile_exception import CompileException
from contract.graph_utils import graph_to_json_string
from transaction.node import Rollback, Write, Variable, Param, Read, If, Node, TYPE

logging.config.fileConfig(fname='logconfig.ini', disable_existing_loggers=False)
_logger = logging.getLogger('contractLogger')


def add_to_dependent_vars(var, node):
    if dependent_vars.get(var) is None:
        dependent_vars[var] = set()
    # print("加入前" + str(dependent_vars[var]))
    dependent_vars[var].add(node)
    # print("加入后" + str(dependent_vars[var]))


def add_to_generate_vars(var, node):
    if generate_vars.get(var) is None:
        generate_vars[var] = set()
    # print(var)
    # print("加入前" + str(generate_vars[var]))
    generate_vars[var].add(node)
    # print("加入后" + str(generate_vars[var]))


# 解析变量中的所有子变量，返回为变量名的列表
def parse_variable(variable):
    # 如果是一个二级引用
    if '$(' in variable:
        # matches.append(variable[2:-1])
        return [variable[2:-1]]
    regex = re.compile(r'\$[a-zA-Z][a-zA-Z0-9_]*')
    matches = regex.findall(variable)
    matches = [match[1:] for match in matches]
    res = []
    for match in matches:
        if ('%s()' % match) not in variable:
            res.append(match)
    return res


# 脚本对象解析器
def parse_script():
    # 处理每一行
    while cur_code_index < len(code_lines):
        # 顶层分析时所有生成节点都需要分配唯一的id
        try:
            parsed_list = parse_one_sentence()
        except BaseException as e:
            if cur_code_index == len(code_lines):
                raise CompileException(cur_code_index + 1, ['if嵌套和fi的数量可能不匹配，请检查'])
            raise CompileException(cur_code_index + 1, ['在第%d行出现了错误' % (cur_code_index + 1)])
        if not parsed_list:
            continue
        for parsed_part in parsed_list:
            # 解析变量生成和依赖关系
            parsed_node, parsed_gen_vars, parsed_dep_vars = parsed_part
            # 记录生成变量情况
            for parsed_gen_var in parsed_gen_vars:
                add_to_generate_vars(parsed_gen_var, parsed_node)
            # 记录依赖变量情况
            for parsed_dep_var in parsed_dep_vars:
                add_to_dependent_vars(parsed_dep_var, parsed_node)


# 解析一条语句，该语句可能是载参、赋值、读和写以及回滚里面中的一种，返回列表[[节点, 变量生成情况， 变量依赖情况]]
# assign_node_id指明是否需要为生成的节点赋值id
def parse_one_sentence():
    global cur_code_index
    if len(code_lines[cur_code_index].strip()) == 0 or code_lines[cur_code_index].strip()[0] == '#':
        # 跳过注释行和空白行
        cur_code_index += 1
        return []
    elif 'loadParam' in code_lines[cur_code_index]:
        return parse_load_param_sentence()
    elif 'if' in code_lines[cur_code_index]:
        return parse_condition_sentence()
    elif 'read' in code_lines[cur_code_index]:
        return parse_read_sentence()
    elif 'write' in code_lines[cur_code_index]:
        return parse_write_sentence()
    elif 'rollback' in code_lines[cur_code_index]:
        return parse_rollback_sentence()
    else:
        # 没有这些特征，说明是赋值语句
        return parse_assignment_sentence()


def parse_load_param_sentence():
    # 载参语句只占用一行
    global cur_code_index, cur_node_index

    line = code_lines[cur_code_index].strip()
    variable = line[10:-1]
    _logger.debug('处理载参语句，载入参数值%s' % variable)
    cur_code_index += 1
    node = Param(0, variable)
    cur_node_index += 1
    node.node_id = str(cur_node_index)

    # 解析变量
    gen_vars = [variable]
    dep_vars = []
    return [[node, gen_vars, dep_vars]]


def parse_assignment_sentence():
    # 赋值语句只占用一行
    global cur_code_index, cur_node_index
    line = code_lines[cur_code_index].strip()
    # print(line)
    var_name, expression = line.split('=')
    # 表达式不可以为\w(
    test = re.findall(r'^\w+\(', expression)
    if len(test) > 0:
        raise BaseException()

    # 去除存在的空白
    var_name = var_name.strip()
    expression = expression.strip()
    _logger.debug('处理赋值语句，将%s赋值给%s' % (expression, var_name))
    cur_code_index += 1

    node = Variable(0, var_name, expression)
    cur_node_index += 1
    node.node_id = str(cur_node_index)
    # node.node_id = pre_define_node_id
    # 解析变量
    # 固定生成一个新变量
    gen_vars = [var_name]
    dep_vars = parse_variable(expression)
    return [[node, gen_vars, dep_vars]]


def parse_condition_sentence():
    global cur_code_index, cur_node_index, context_node_id
    # IF一定是顶层语句
    cur_node_index += 1
    node = If(str(cur_node_index))

    # 解析条件
    line = code_lines[cur_code_index].strip()[2:-4]

    condition = line.strip()
    node.conditions = condition
    cur_code_index += 1
    _logger.debug('处理条件语句，为真条件为%s' % condition)

    # 解析变量
    gen_vars = []
    dep_vars = []

    # 处理条件的解析
    dep_vars += parse_variable(condition)

    # 处理内部语句
    node.true_sub_node_list = []
    # 处理if满足的所有语句
    while code_lines[cur_code_index].strip() != 'else' and code_lines[cur_code_index].strip() != 'fi':
        # pre_context_node_id = context_node_id
        # context_node_id = cur_node_index
        parsed_list = parse_one_sentence()
        # context_node_id = pre_context_node_id
        # if not parsed_list:
        #     continue
        for parsed_part in parsed_list:
            # 分别是代表的节点，节点生成变量，节点依赖变量
            parsed_node, parsed_gen_vars, parsed_dep_vars = parsed_part
            node.true_sub_node_list.append(parsed_node)
            gen_vars += parsed_gen_vars
            dep_vars += parsed_dep_vars
        # code_index += 1
    # 如果没有else，离开即可，离开时需要扔掉最后那个
    if 'else' not in code_lines[cur_code_index]:
        node.false_sub_node_list = list()
        _logger.debug('条件处理结束')
        cur_code_index += 1
        return [[node, gen_vars, dep_vars]]
    # 继续处理else时的所有语句
    # 首先跳过这个else
    cur_code_index += 1
    # node.else_node = If(0)
    while code_lines[cur_code_index].strip() != 'fi':
        # pre_context_node_id = context_node_id
        # context_node_id = cur_node_index
        parsed_list = parse_one_sentence()
        # context_node_id = pre_context_node_id
        # if not parsed_list:
        #     continue
        for parsed_part in parsed_list:
            # 分别是代表的节点，节点生成变量，节点依赖变量
            parsed_node, parsed_gen_vars, parsed_dep_vars = parsed_part
            node.false_sub_node_list.append(parsed_node)
            gen_vars += parsed_gen_vars
            dep_vars += parsed_dep_vars
    # 扔掉最后那个end
    cur_code_index += 1
    _logger.debug('条件处理结束')

    return [[node, gen_vars, dep_vars]]


def parse_read_sentence():
    # 读取语句只占用一行
    global cur_code_index, cur_node_index
    line = code_lines[cur_code_index]
    # 解析变量名和右侧阅读语句细节
    variable, right_exp = line.split('=')
    right_exp = right_exp[5:-1]
    # 解析链id和key
    chain_id, key = right_exp.split(',')
    if chain_id[0] == '(':
        chain_id = chain_id[1:]
    # 去掉可能存在的空白
    variable = variable.strip()
    chain_id = chain_id.strip()
    key = key.strip()
    # 需要带上链标识
    # key = '%s-%s' % (chain_id, key.strip())
    _logger.debug('处理读取语句，将从%s读取到的%s的值写入变量%s中' % (chain_id, key, variable))
    cur_code_index += 1
    read_node = Read(0, chain_id, key, variable)

    # 每个Read语句生成一个节点，一个赋值语句，一个阅读语句
    cur_node_index += 1
    read_node.node_id = str(cur_node_index)
    # 解析变量
    # 解析阅读变量
    read_gen_vars = [variable]
    read_dep_vars = parse_variable(key)
    return [[read_node, read_gen_vars, read_dep_vars]]


def parse_write_sentence():
    # 写入语句只占用一行
    global cur_code_index, cur_node_index
    line = code_lines[cur_code_index].strip()
    line = line[6:-1]
    chain_id, key, value = line.split(',')
    # 去除可能存在的空白
    chain_id = chain_id.strip()
    key = key.strip()
    value = value.strip()
    _logger.debug('处理写入语句，将key-%s，value-%s写入链%s' % (key, value, chain_id))
    cur_code_index += 1
    # 每个Write语句会生成两个节点，一个Read节点读取旧值，一个Write读取
    read_node = Read(0, chain_id, key, None, True)
    write_node = Write(0, chain_id, key, value)
    cur_node_index += 2
    read_node.node_id = str(cur_node_index - 1)
    write_node.node_id = str(cur_node_index)
    # 解析read_node的变量依赖
    # read_gen_vars = ['%s-%s' % (write_node.node_id, key)]
    read_gen_vars = ['%s-%s' % (write_node.node_id, key)]
    read_dep_vars = parse_variable(key)
    # 解析write_node的变量依赖
    write_gen_vars = []
    # write_dep_vars = ['%s-%s' % (write_node.node_id, key)] + parse_variable(value) + parse_variable(key)
    write_dep_vars = ['%s-%s' % (write_node.node_id, key)] + parse_variable(value) + parse_variable(key)
    # write_dep_vars = []
    return [[read_node, read_gen_vars, read_dep_vars], [write_node, write_gen_vars, write_dep_vars]]


def parse_rollback_sentence():
    # 回滚语句只占用一行
    global cur_code_index, cur_node_index

    _logger.debug('处理回滚语句')
    cur_code_index += 1
    node = Rollback(0)
    cur_node_index += 1
    node.node_id = str(cur_node_index)
    return [[node, [], []]]


# 行数和行数索引
code_lines = []
cur_code_index = 0

# 保存变量的生成和依赖的节点，不能有自环
generate_vars = {}
dependent_vars = {}
# context_node_id = 0
# 当前的节点编号
cur_node_index = 0


# 对代码进行解析
def parse_code(code: str):
    global code_lines, cur_code_index, generate_vars, dependent_vars, cur_node_index, context_node_id
    context_node_id = 0
    cur_node_index = 0
    generate_vars = dict()
    dependent_vars = dict()
    # 对代码切割成很多行
    code_lines = code.split("\n")
    cur_code_index = 0
    # print(code_lines)
    # 解析脚本
    parse_script()
    # print(dependent_vars)
    # 找到起始节点，起始节点一定是所有生成变量的节点中序号最小的那一个
    starts = list()
    # 由生成变量的节点指向依赖变量的节点
    variables = set(dependent_vars.keys()) | set(generate_vars.keys())
    for variable in variables:
        # 所有生成节点按照id排序
        gen_vars = sorted(list(generate_vars[variable]), key=lambda n: int(n.node_id))
        starts.append(gen_vars[0])
        # 所有依赖节点按照id排序
        dep_vars = sorted(list(dependent_vars[variable]), key=lambda n: int(n.node_id))

        # 生成节点间存在顺序依赖，连续的依赖节点可以并行执行
        dep_index = 0

        # 总体上寻找生成节点间的顺序关系，然后在各生成节点间插入若干依赖节点，这些依赖节点可以并行执行
        for i in range(1, len(gen_vars)):
            # gen_vars[i-1]指向gen_vars[i]
            gen_vars[i].parents.add(gen_vars[i - 1])
            gen_vars[i - 1].children.add(gen_vars[i])
            # 当gen_vars[i - 1].node_id < dep_vars[dep_index].node_id < gen_vars[i].node_id时
            while dep_index < len(dep_vars) and \
                    int(gen_vars[i - 1].node_id) <= int(dep_vars[dep_index].node_id) <= int(gen_vars[i].node_id):
                if gen_vars[i - 1].node_id == dep_vars[dep_index].node_id \
                        or gen_vars[i].node_id == dep_vars[dep_index].node_id:
                    dep_index += 1
                    continue
                # 将三者串联，++ dep_index
                gen_vars[i].parents.add(dep_vars[dep_index])
                dep_vars[dep_index].children.add(gen_vars[i])
                dep_vars[dep_index].parents.add(gen_vars[i - 1])
                gen_vars[i - 1].children.add(dep_vars[dep_index])
                dep_index += 1
        # 如果仍有部分依赖节点没有连接，全部由最后一个生成节点指向
        while dep_index < len(dep_vars):
            if dep_vars[dep_index].node_id == gen_vars[len(gen_vars) - 1].node_id:
                dep_index += 1
                continue
            dep_vars[dep_index].parents.add(gen_vars[len(gen_vars) - 1])
            gen_vars[len(gen_vars) - 1].children.add(dep_vars[dep_index])
            dep_index += 1

    # for variable in generate_vars.keys():
    #     gen_nodes = list(generate_vars[variable])
    #     gen_nodes = sorted(gen_nodes, key=lambda n: n.node_id)
    #     starts.append(gen_nodes[0])
    return starts


if __name__ == '__main__':
    # print(parse_variable('$input_merchant_id'))
    # print(parse_variable('$fish_id:_temperature'))
    # print(parse_variable('$temperature<0'))
    # print(parse_variable('$fish_id:$temperature'))
    # exit()

    code = '''
loadParam(code)
component_count = read(0x0001, component_count_:$code)
if $component_count < 3 then
    rollback
else
    product_order = $component_count / 3
fi
write(0x0002, product_by_:$code, $product_order)
    '''
    res = parse_code(code)
    # print(res)
    print(graph_to_json_string(res))
    # print(nodes)
    # print(len(nodes))
    # for node in nodes:
    #     print(node.to_dict())
    # #
    # # print(dependent_vars)
    # # print(generate_vars)
    #
    # keys = set(dependent_vars.keys()) | set(generate_vars.keys())
    # for key in keys:
    #     print('# %s' % key)
    #     print(list([] if generate_vars.get(key) is None else list(generate_vars[key])))
    #     print(list([] if dependent_vars.get(key) is None else list(dependent_vars[key])))
