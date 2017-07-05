#!/usr/bin/evn python3.5.3
# -*- coding: utf-8 -*-
'''
当前是日线数据
从csv数据中读取并存到bcolz数据中
'''
import bcolz
import pandas as pd
import numpy as np

index_path = 'day_index.csv'
print("读取索引文件:" + index_path)
arr = pd.read_csv(index_path)
code_list = arr['code']
print("一共有", len(code_list), "数据文件")
sum = None
line_map = {}
beg = 0
end = 0
index = 0
for code in code_list:
    print(code)
    arr = pd.read_csv('day_' + code + '.csv', usecols=[1, 2, 3, 4, 5, 6, 7, 8, 9])
    if index == 0:
        sum = arr
    else:
        sum = pd.concat([sum, arr], ignore_index=True)
    end = len(sum)
    line_map[code] = [beg, end]
    beg = end
    index += 1
dst_path = 'test001.bcolz'
ct = bcolz.ctable.fromdataframe(sum, rootdir=dst_path, mode='w')
ct.attrs['line_map'] = line_map
ct.flush()
print("保存到" + dst_path + "完成")