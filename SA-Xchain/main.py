import json
import logging.config
from run_test import run_test

logging.config.fileConfig(fname='logconfig.ini', disable_existing_loggers=False)
_logger = logging.getLogger('testLogger')

if __name__ == '__main__':
    # 编译提交的代码
    _logger.info('读取用户提交的脚本')
    # TODO 修改方式，这里假设从文本文档中读取
    with open('./scene1.sh', 'r') as fp:
        code = fp.read()
    with open("scene1.json", 'r') as fp:
        data1 = json.load(fp)

    result = run_test('000000000000', code, data1)

    if result.result != 0:
        if result.result == 2:
            print(result.compile)
            exit()
        print(result.result)
        print('%s/%s' % (result.count, result.all))
        for (i, case) in enumerate(result.cases):
            for o in case.output:
                print(o)
    else:
        print('场景1通过')

    with open('./scene2.sh', 'r') as fp:
        code = fp.read()

    with open("scene2.json", 'r') as fp:
        data2 = json.load(fp)

    result = run_test('000000000000', code, data2)
    if result.result != 0:
        if result.result == 2:
            print(result.compile)
            exit()
        print(result.result)
        print('%s/%s' % (result.count, result.all))
        for (i, case) in enumerate(result.cases):
            for o in case.output:
                print(o)
    else:
        print('场景2通过')

    with open('./scene2_1.sh', 'r') as fp:
        code = fp.read()

    result = run_test('000000000000', code, data2)
    if result.result != 0:
        if result.result == 2:
            print(result.compile)
            exit()
        print(result.result)
        print('%s/%s' % (result.count, result.all))
        for (i, case) in enumerate(result.cases):
            for o in case.output:
                print(o)
    else:
        print('场景2_1通过')

    with open('./scene2_2.sh', 'r') as fp:
        code = fp.read()

    result = run_test('000000000000', code, data2)
    if result.result != 0:
        if result.result == 2:
            print(result.compile)
            exit()
        print(result.result)
        print('%s/%s' % (result.count, result.all))
        for (i, case) in enumerate(result.cases):
            for o in case.output:
                print(o)
    else:
        print('场景2_2通过')

    with open("scene2.json", 'r') as fp:
        data2 = json.load(fp)

    with open('./scene2_3.sh', 'r') as fp:
        code = fp.read()

    result = run_test('000000000000', code, data2)
    if result.result != 0:
        if result.result == 2:
            print(result.compile)
            exit()
        print(result.result)
        print('%s/%s' % (result.count, result.all))
        for (i, case) in enumerate(result.cases):
            for o in case.output:
                print(o)
    else:
        print('场景2_3通过')