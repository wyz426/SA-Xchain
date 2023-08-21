#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Filename:compile_exception
# @Author:zekdot
# @Time: 2023/3/30 下午1:13
class CompileException(Exception):

    def __init__(self, line: int, info: list):
        # 出错的行数
        self.line = line
        # 出错的信息
        self.info = info


if __name__ == '__main__':
    print('Hello World');
