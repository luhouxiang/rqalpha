#!/usr/bin/evn python3.5.3
# -*- coding: utf-8 -*-
'''
当前是分钟线数据
从bcolz数据中读取并存到cvs数据中
最终存成一支股票一个csv文件,所有的股票代码存于索引文件index_index.csv中
'''

import bcolz
from collections import namedtuple
import numpy as np
import pandas as pd

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

def _remove_(l, v):
    try:
        l.remove(v)
    except ValueError:
        pass

rootdirs_stocks_mb = ["date", "time", "open", "close", "high", "low",
                      "total_turnover", "volume", "limit_up", "limit_down"]
rootdirs_stocks_mb_index = ["date", "start_at", "end_at"]
path = 'E:\\hq-data\\rqalpha-plus\\.rqalpha-plus\\bundle\\'

# 索引文件
filename = 'stocks_mb_index.bcolz'
mb_index_path = path + filename
print("打开索引文件：" + mb_index_path)
_index_table = bcolz.open(mb_index_path, 'a')
_index_index_ = _index_table.attrs['line_map']

# 数据文件
filename= 'stocks_mb' + '.bcolz'
mb_path =(path + filename)
print("打开数据文件：" + mb_path)
_table = bcolz.open(mb_path, 'a')
_index = _table.attrs['end_date']

_converter = StockBarConverter
index_fields = _index_table.names[0:]
table_fields = _table.names[0:]
dtype = np.dtype([(f, _converter.field_type(f, _table.cols[f].dtype))
                  for f in table_fields])
stock_list = []
stock_type = np.dtype({'names':['name'], 'formats':['S32']}, align=True)
count = 0
print("一共有股票", len(_index_index_), "支股票需要保存成.csv文件")
for code, value in _index_index_.items():
    stocks = []
    stocks.append(code)
    stock_list.append(stocks)
    count += 1
    s, e = value
    date_list = _index_table.cols[index_fields[0]][s:e]
    start_list = _index_table.cols[index_fields[1]][s:e]
    end_list = _index_table.cols[index_fields[2]][s:e]
    sum_result = None
    date_list_len = len(date_list)
    if date_list_len > 200:
        print(code + ': ', "*" * int(date_list_len/200 + 1))
    for i in range(date_list_len):
        s = start_list[i]
        e = end_list[i]
        result = np.empty(shape=(e - s,), dtype=dtype)
        for f in table_fields:
            result[f] = _converter.convert(f, _table.cols[f][s:e])
        if i == 0:
            sum_result = result
        else:
            sum_result = np.concatenate((sum_result, result))

        if i > 0 and (i % 200) == 0:
            print(code + ': ', "." * int(i / 200 + 1))
    # 保存每一支股票的分钟线到.csv中
    dst_path = 'minute_' + code + '.csv'
    # np.savetxt(dst_path, sum, delimiter=',')
    df = pd.DataFrame(data=sum_result, columns=table_fields)
    df.to_csv(dst_path)
    print("[", count, "/", len(_index_index_), "]", "保存文件:", dst_path)
    if count >= 3:
        break

dst_path = "minute_index.csv"
df = pd.DataFrame(data=stock_list, columns=['code'])
df.to_csv(dst_path)
# np.savetxt(dst_path, stockarr, delimiter=',', fmt="%s")
print("保存索引文件", dst_path, "成功，数据保存完成")
