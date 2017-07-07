#!/usr/bin/evn python3.5.3
# -*- coding: utf-8 -*-
'''
当前是日线数据
从csv数据中读取并存到bcolz数据中
'''
import bcolz
import pandas as pd

index_path = 'day_index.csv'
print("读取索引文件:" + index_path)
arr = pd.read_csv(index_path)
code_list = arr['code']
print("一共有", len(code_list), "数据文件")
line_map = {}
beg = 0
end = 0
index = 0
dst_path = 'test001.bcolz'
for code in code_list:
    print(code)
    arr = pd.read_csv('day_' + code + '.csv', usecols=[1, 2, 3, 4, 5, 6, 7, 8, 9])
    end = len(arr)
    if index == 0:
        index = 1
        ct = bcolz.ctable.fromdataframe(arr, rootdir=dst_path, mode='w')
        ct.flush()
        ct = bcolz.open(rootdir=dst_path, mode='a')
    else:
        tt = bcolz.ctable.fromdataframe(arr)
        ct.append(tt)
    line_map[code] = [beg, end]
    beg = end

ct.attrs['line_map'] = line_map
ct.flush()
print("保存到" + dst_path + "完成")
