#!/usr/bin/env python
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
import numpy as np
from rqalpha.data.base_data_source import BaseDataSource
from rqalpha.data.converter import StockBarConverter, IndexBarConverter
from rqalpha.utils.datetime_func import convert_dt_to_int, convert_int_to_date
from rqalpha.utils.py2 import lru_cache
from .minutebar_store import MinuteBarStore

class MinuteDataSource(BaseDataSource):
    def __init__(self, env):
        path = env.config.base.data_bundle_path
        super(MinuteDataSource, self).__init__(path)
        self._minute_bars = [
            MinuteBarStore('E:\\hq-data\\rqalpha-plus\\.rqalpha-plus\\bundle\\stocks_mb.bcolz',
                           'E:\\hq-data\\rqalpha-plus\\.rqalpha-plus\\bundle\\stocks_mb_index.bcolz',
                           StockBarConverter),
            MinuteBarStore('E:\\hq-data\\rqalpha-plus\\.rqalpha-plus\\bundle\\indexes_mb.bcolz',
                           'E:\\hq-data\\rqalpha-plus\\.rqalpha-plus\\bundle\\indexes_mb_index.bcolz',
                           IndexBarConverter),
        ]

    def get_bar(self, instrument, dt, frequency):
        if frequency == '1d':
            return super(MinuteDataSource, self).get_bar(instrument, dt, frequency)
        bars = self._all_minute_bars_of(instrument, dt)
        if bars is None:
            return None
        dt = np.uint64(convert_dt_to_int(dt))
        pos = bars['datetime'].searchsorted(dt)
        if pos >= len(bars) or bars['datetime'][pos] != dt:
            return None
        return bars[pos]

    def history_bars(self, instrument, bar_count, frequency, fields, dt,
                     skip_suspended=True, include_now=False,
                     adjust_type='pre', adjust_orig=None):
        if frequency == '1d':
            return super(MinuteDataSource, self).history_bars(instrument, bar_count, frequency, fields, dt,
                                                              skip_suspended, include_now, adjust_type, adjust_orig)

    @lru_cache(None)
    def _all_minute_bars_of(self, instrument, dt):
        i = self._index_of(instrument)
        return self._minute_bars[i].get_bars(instrument.order_book_id, dt, fields=None)

    def available_data_range(self, frequency):
        if frequency in ['tick', '1d', '1m']:
            s, e = self._day_bars[self.INSTRUMENT_TYPE_MAP['INDX']].get_date_range('000001.XSHG')
            return convert_int_to_date(s).date(), convert_int_to_date(e).date()
        raise NotImplementedError
