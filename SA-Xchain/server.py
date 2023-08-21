#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Filename:server.py
# @Author:zekdot
# @Time: 2023/3/31 上午2:55
import json
from copy import deepcopy

from flask import Flask, request

from run_test import run_test as run_one

app = Flask(__name__)

legal_code_list =  ['662977146', '631419353', '135660402', '839989072', '946544814', '386227244', '101599600',
                    '674871201', '176201269', '262098992', '378110184', '506732109']


with open("scene0.txt", "r") as fp:
    topic0 = fp.read()

with open("scene1.txt", "r") as fp:
    topic1 = fp.read()

with open("scene2.txt", "r") as fp:
    topic2 = fp.read()


# 读取参数
with open("scene0.json", 'r') as fp:
    data0 = json.load(fp)

with open("scene1.json", 'r') as fp:
    data1 = json.load(fp)

with open("scene2.json", 'r') as fp:
    data2 = json.load(fp)


@app.route('/validate_code')
def validate_code():
    usercode = request.args.get('usercode')
    if usercode not in legal_code_list:
        return "invalid"
    return "valid"


@app.route('/read_scene')
def read_scene():
    usercode = request.args.get('usercode')
    if usercode == '000000000':
        return topic0
    if usercode not in legal_code_list:
        return "您的测试码不正确"
    # 前半部分展示第一题，后半部分展示第二题
    index = legal_code_list.index(usercode)
    if index < len(legal_code_list) // 2:
        return topic1
    return topic2


@app.route('/run_test', methods=["POST"])
def run_test():
    usercode = request.json.get('usercode')
    if usercode == '000000000':
        code = request.json.get('code')
        try:
            return json.dumps(run_one(usercode, code, deepcopy(data0)).to_dict())
        except KeyError as e:
            # print(e)
            return json.dumps(
                {"result": 2, "count": 0, "all": 0, "compile_info": [0, "变量%s在声明前引用" % e.args[0]],
                 "cases": None})
        except BaseException as e:
            raise e
    if usercode not in legal_code_list:
        return "您的测试码不正确"
    code = request.json.get('code')
    # 前半部分做第一题，后半部分做第二题
    index = legal_code_list.index(usercode)
    try:
        if index < len(legal_code_list) // 2:
            return json.dumps(run_one(usercode, code, deepcopy(data1)).to_dict())
        return json.dumps(run_one(usercode, code, deepcopy(data2)).to_dict())
    except KeyError as e:
        # raise e
        return json.dumps(
            {"result": 2, "count": 0, "all": 0, "compile_info": [0, "变量%s在声明前引用" % e.args[0]],
             "cases": None})
    except BaseException as e:
        raise e
        # return json.dumps({"result": 2, "count": 0, "all": 0, "compile_info": [0, "未知错误，可能是在引用变量前没有声明"], "cases": None})


@app.route('/record_result', methods=["POST"])
def record_result():
    result = request.json.get('result')
    with open('result.txt', 'a') as fp:
        fp.write(result)
        fp.write('\n')
    return "success"


if __name__ == '__main__':
    from gevent import pywsgi

    server = pywsgi.WSGIServer(('localhost', 5000), app)
    print('server start')
    server.serve_forever()
