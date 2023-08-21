#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Filename:exp_parse
# @Author:zekdot
# @Time: 2023/1/27 上午10:41


# 实现字符串的拼接
def _concat_str(exp: str) -> str:
    # 处理字符串拼接，这里直接忽略冒号就可以实现
    while ':' in exp:
        exp = exp.replace(':', '')
    return exp


def add_str_func(exp: str, mark: str):
    rep_mark = '==' if mark == '##' else '!='
    while mark in exp:
        # 替换左边
        point = exp.index(mark) - 1
        while exp[point] == ' ':
            point -= 1
        # 左表达式结束位置
        lend = point + 1
        while point >= 0 and exp[point] != ' ':
            point -= 1
        # 左表达式开始位置
        lstart = point + 1
        # 替换右边
        point = exp.index(mark) + 2
        while exp[point] == ' ':
            point += 1
        # 右表达式开始位置
        rstart = point
        while point < len(exp) and exp[point] != ' ':
            point += 1
        rend = point
        # 进行一次替换
        exp = exp[0:lstart] + "str('%s')" % exp[lstart:lend] + rep_mark + "str('%s')" % exp[rstart:rend] + exp[rend:]
    return exp


# 计算表达式的值
def _calc_exp(exp: str) -> str:
    # 如果有字符串比较，需要进行替换
    exp = add_str_func(exp, '##')
    exp = add_str_func(exp, '!#')
    # 如果有:就肯定是一个字符串拼接
    if ':' in exp:
        return _concat_str(exp)
    # 如果有加减乘除或者逻辑表达式，就调用eval进行计算，返回值肯定是一个非字符串变量
    if '+' in exp or '-' in exp or '*' in exp or '/' in exp or ' and ' in exp or ' or ' in exp or ' not ' in exp \
            or '==' in exp or '!=' in exp or '<' in exp or '>' in exp or '>=' in exp or '<=' in exp:
        try:
            return eval(exp)
        except:
            return exp
    # 都没有，就直接返回
    return exp


# 辅助实现表达式解析
idx = 0


def _parse_exp_helper(exp: str, var_pool: dict, func_pool: dict):
    global idx
    left_bracket_num = 0
    res = ''
    while idx < len(exp):
        if exp[idx] == '$':
            # 处理下一个字符
            idx += 1
            # 需要解析子表达式
            if exp[idx] == '(':
                # 处理下一个字符
                idx += 1
                # 解析出的是一个子key
                sub_key = _parse_exp_helper(exp, var_pool, func_pool)
                # 将这个子key对应的值加入结果中
                # 从变量池取出对应值
                res += str(var_pool[sub_key])
            # 否则解析到一个不是字母或下划线的字符为止
            else:
                key = ''
                while idx < len(exp) and (exp[idx].isalnum() or exp[idx] == '_' or exp[idx] == '('):
                    key += exp[idx]
                    idx += 1
                # 判断要处理的是否是方法
                if key[-1] == '(':
                    # 不需要回退了，因为接下来是方法的右括号
                    res += str(func_pool[key + ')']())
                else:
                    # 回退一格，作为下一个要处理的变量
                    idx -= 1
                    # 从方法池取出对应值
                    res += str(var_pool[key])
        elif exp[idx] == '(':
            left_bracket_num += 1
            res += '('
        elif exp[idx] == ')':
            # 如果前面有匹配括号，是表达式一部分
            if left_bracket_num > 0:
                left_bracket_num -= 1
                res += ')'
            # 否则说明是子变量引用表达式，离开循环，计算表达式的字符串值并返回上一层
            else:
                # 跳过这个括号
                idx += 1
                break
        else:
            res += exp[idx]
        idx += 1

    # 返回计算结果
    return _calc_exp(res)


# 对表达式的解析，解析需要根据变量池和表达式一同解析出结果
# 解析表达式
def parse_exp(exp: str, var_pool: dict, func_pool: dict):
    exp = str(exp)
    # 如果没有间接引用，直接计算即可
    if '$' not in exp:
        return _calc_exp(exp)
    # 否则需要处理间接引用然后再计算
    global idx
    idx = 0
    parse_res = _parse_exp_helper(exp, var_pool, func_pool)
    return parse_res


if __name__ == '__main__':
    print(parse_exp('fish_id:1234:$x', {'x': 213}, {}))
    print(parse_exp('fish_id', {}, {}))
    print(parse_exp('15465456', {}, {}))
    print(parse_exp('$fisher_id', {'fisher_id': '231242'}, {}))
    print(parse_exp('$fish_id:process_method', {'fish_id': '123654'}, {}))
    print(parse_exp('$cost_time + $now()', {'cost_time': 4564564}, {'now()': lambda: 13243243}))
    print(parse_exp('$($fish_id:temperature)', {'fish_id': '123654', '123654temperature': 16}, {}))
    print(parse_exp('40+52', {}, {}))
    print(parse_exp('$fish_type==123', {'fish_type': 456}, {}))
    print(parse_exp('($temperature<10 and $temperature>=5) or $fish_type==123', {'temperature': 8, 'fish_type': 456}, {}))
