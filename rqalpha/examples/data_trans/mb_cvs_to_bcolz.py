#!/usr/bin/evn python3.5.3
# -*- coding: utf-8 -*-
'''
当前是分钟线数据
从csv数据中读取并存到bcolz数据中
'''
import bcolz
import pandas as pd

index_path = 'minute_index.csv'
print("读取索引文件:" + index_path)
arr = pd.read_csv(index_path, usecols=[1, 2, 3])
code_list = arr['code']
mb_index_list = []
date_list = []
date_dict = {}
print("一共有", len(code_list), "数据文件")
line_map = {}
end_date = {}
index = 0
l_s, l_e = 0, 0
dst_path = "mb_stock.bcolz"
for code in code_list:
    print(code)
    arr = pd.read_csv('minute_' + code + '.csv', usecols=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    date_list.clear() # 每支股票开始时，清理数据
    date_dict.clear()
    for date in arr['date']:
        if date not in date_list:
            date_list.append(date)
            date_dict[date] = 1
        else:
            date_dict[date] += 1
    s, e = 0, 0
    for date in date_list:
        index_items = []
        index_items.append(date)
        e += date_dict[date]
        index_items.append(s)
        index_items.append(e)
        s = e
        mb_index_list.append(index_items)
    l_e += len(date_list)
    line_map[code] = [l_s, l_e]
    l_s = l_e
    end_date[code] = int(date_list[-1])

    if index == 0:
        index = 1
        ct = bcolz.ctable.fromdataframe(arr, rootdir=dst_path, mode='w')
        ct.flush()
        ct = bcolz.open(rootdir=dst_path, mode='a')
    else:
        tt = bcolz.ctable.fromdataframe(arr)
        ct.append(tt)

ct.attrs['end_date'] = end_date
ct.flush()
print("保存到" + dst_path + "完成")
index_df = pd.DataFrame(data=mb_index_list, columns=['date', 'start_at', 'end_at'])
dst_index_path = 'mb_stock_index.bcolz'
index_ct = bcolz.ctable.fromdataframe(index_df, rootdir=dst_index_path, mode='w')
index_ct.attrs['line_map'] = line_map
index_ct.flush()
print("保存到" + dst_index_path + "完成")


