#!/usr/bin/evn python3.5.3
# -*- coding: utf-8 -*-
'''
当前是日线数据
从bcolz数据中读取并存到cvs数据中
最终存成一支股票一个csv文件,所有的股票代码存于索引文件.csv中
'''

import pandas as pd
from pandas import DataFrame,Series
import bcolz
from collections import namedtuple
import numpy as np

Rule = namedtuple('Rule', ['dtype', 'multiplier', 'round'])
class Converter(object):
    def __init__(self, rules):
        self._rules = rules

    def convert(self, name, data):
        try:
            r = self._rules[name]
        except KeyError:
            return data

        result = data * r.multiplier
        if r.round:
            result = np.round(result, r.round)

        return result

    def field_type(self, name, dt):
        try:
            return self._rules[name].dtype
        except KeyError:
            return dt

float64 = np.dtype('float64')

StockBarConverter = Converter({
    'open': Rule(float64, 1 / 10000.0, 2),
    'close': Rule(float64, 1 / 10000.0, 2),
    'high': Rule(float64, 1 / 10000.0, 2),
    'low': Rule(float64, 1 / 10000.0, 2),
    'limit_up': Rule(float64, 1/10000.0, 2),
    'limit_down': Rule(float64, 1/10000.0, 2),
    'volume': Rule(float64, 1, 0),
})


path = 'C:\\Users\\Administrator\\.rqalpha\\bundle\\'

def _remove_(l, v):
    try:
        l.remove(v)
    except ValueError:
        pass

day_path = path + "stocks.bcolz"
print("打开数据文件：" + day_path)
_table = bcolz.open(day_path, 'a')
_index = _table.attrs['line_map']
_converter = StockBarConverter

print("一共有股票", len(_index), "支股票需要保存成.csv文件")
fields = _table.names[0:]
dtype = np.dtype([(f, _converter.field_type(f, _table.cols[f].dtype))
                  for f in fields])

stock_list = []
for code, value in _index.items():
    stocks = []
    stocks.append(code)
    stock_list.append(stocks)
    s, e = value
    result = np.empty(shape=(e - s,), dtype=dtype)
    for f in fields:
        result[f] = _converter.convert(f, _table.cols[f][s:e])

    arr = []
    for idx1, cache in enumerate(result):
        list = []
        for idx2, val in enumerate(cache):
            list.append(val)
        arr.append(list)

    df = DataFrame(data=arr,columns=fields)
    dst_path = 'day_' + code + '.csv'
    df.to_csv(dst_path)
    print("[", len(stock_list), "/", len(_index), "]", "保存文件:", dst_path)
    # TODO: 测试代码，正式用前应将后面的判断去除
    if len(stock_list) > 3:
        break

df = DataFrame(data=stock_list, columns=['code'])
dst_path = 'day_index.csv'
df.to_csv(dst_path)
print("保存索引文件" + dst_path + "成功，数据保存完成")