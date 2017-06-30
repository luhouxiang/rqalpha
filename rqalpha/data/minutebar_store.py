# -*- coding: utf-8 -*-
#
# Copyright 2017 Ricequant, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 分钟线存储

import bcolz
import numpy as np
import six

from ..utils.i18n import gettext as _
from ..utils.datetime_func import convert_date_to_int

class MinuteBarStore(object):
    def __init__(self, main, main_index, converter):
        self._table = bcolz.open(main, 'r')
        self._index_table = bcolz.open(main_index, 'r')
        self._index_index = self._index_table.attrs['line_map']
        self._index = {}
        self._converter = converter
        for key, lists in self._index_index.items():
            s, e = self._index_index[key]
            date_day = self._index_table.cols['date'][s:e]
            start_at = self._index_table.cols['start_at'][s:e]
            end_at = self._index_table.cols['end_at'][s:e]
            # self._index[key][date_day] = [start_at[0], end_at[-1]]
            self._index[key] = {}
            for i in range(0, len(date_day)):
                self._index[key][date_day[i]] = [start_at[i], end_at[i]]



    @staticmethod
    def _remove_(l, v):
        try:
            l.remove(v)
        except ValueError:
            pass

    def get_bars(self, order_book_id, dt, fields=None):
        try:
            idate = np.uint64(convert_date_to_int(dt))
            day = (int)(idate/1000000)
            time = (int)(idate%1000000)
            s, e = self._index[order_book_id][day]
        except KeyError:
            six.print_(_(u"No data for {}").format(order_book_id))
            return

        if fields is None:
            # the first is date
            fields = self._table.names[1:]

        if len(fields) == 1:
            return self._converter.convert(fields[0], self._table.cols[fields[0]][s:e])

        # remove datetime if exist in fields
        self._remove_(fields, 'datetime')

        dtype = np.dtype([('datetime', np.uint64)] +
                         [(f, self._converter.field_type(f, self._table.cols[f].dtype))
                          for f in fields])
        result = np.empty(shape=(e - s, ), dtype=dtype)
        for f in fields:
            result[f] = self._converter.convert(f, self._table.cols[f][s:e])
        result['datetime'] = self._table.cols['date'][s:e]
        result['datetime'] *= 1000000
        result['datetime'] += result['time']

        return result

    def get_date_range(self, order_book_id):
        s, e = self._index[order_book_id]
        return self._table.cols['date'][s], self._table.cols['date'][e - 1]
