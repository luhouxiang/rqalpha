# -*- coding: utf-8 -*-
#
# Copyright 2019 Ricequant, Inc
#
# * Commercial Usage: please contact public@ricequant.com
# * Non-Commercial Usage:
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

import datetime

import numpy as np

from rqalpha.environment import Environment
from rqalpha.utils.logger import system_log
from rqalpha.utils.datetime_func import convert_int_to_datetime, convert_ms_int_to_datetime


class TickObject(object):
    def __init__(self, instrument, tick_dict):
        """
        Tick 对象
        :param instrument: Instrument
        :param tick_dict: dict
        """
        self._instrument = instrument
        self._tick_dict = tick_dict

    @property
    def order_book_id(self):
        """
        [str] 标的代码
        """
        return self._instrument.order_book_id

    @property
    def datetime(self):
        """
        [datetime.datetime] 当前快照数据的时间戳
        """
        try:
            dt = self._tick_dict['datetime']
        except (KeyError, ValueError):
            return datetime.datetime.min
        else:
            if not isinstance(dt, datetime.datetime):
                if dt > 10000000000000000:  # ms
                    return convert_ms_int_to_datetime(dt)
                else:
                    return convert_int_to_datetime(dt)
            return dt

    @property
    def open(self):
        """
        [float] 当日开盘价
        """
        return self._tick_dict['open']

    @property
    def last(self):
        """
        [float] 当前最新价
        """
        return self._tick_dict['last']

    @property
    def high(self):
        """
        [float] 截止到当前的最高价
        """
        return self._tick_dict['high']

    @property
    def low(self):
        """
        [float] 截止到当前的最低价
        """
        return self._tick_dict['low']

    @property
    def prev_close(self):
        """
       [float] 昨日收盘价
       """
        try:
            return self._tick_dict['prev_close']
        except (KeyError, ValueError):
            return 0

    @property
    def volume(self):
        """
        [float] 截止到当前的成交量
        """
        try:
            return self._tick_dict['volume']
        except (KeyError, ValueError):
            return 0

    @property
    def total_turnover(self):
        """
        [float] 截止到当前的成交额
        """
        try:
            return self._tick_dict['total_turnover']
        except (KeyError, ValueError):
            return 0

    @property
    def open_interest(self):
        """
        [float] 截止到当前的持仓量（期货专用）
        """
        try:
            return self._tick_dict['open_interest']
        except (KeyError, ValueError):
            return 0

    @property
    def prev_settlement(self):
        """
        [float] 昨日结算价（期货专用）
        """
        try:
            return self._tick_dict['prev_settlement']
        except (KeyError, ValueError):
            return 0

    @property
    def asks(self):
        """
        [list] 卖出报盘价格，asks[0]代表盘口卖一档报盘价
        """
        try:
            return self._tick_dict['asks']
        except (KeyError, ValueError):
            return [0] * 5

    @property
    def ask_vols(self):
        """
        [list] 卖出报盘数量，ask_vols[0]代表盘口卖一档报盘数量
        """
        try:
            return self._tick_dict['ask_vols']
        except (KeyError, ValueError):
            return [0] * 5

    @property
    def bids(self):
        """
        [list] 买入报盘价格，bids[0]代表盘口买一档报盘价
        """
        try:
            return self._tick_dict['bids']
        except (KeyError, ValueError):
            return [0] * 5

    @property
    def bid_vols(self):
        """
        [list] 买入报盘数量，bids_vols[0]代表盘口买一档报盘数量
        """
        try:
            return self._tick_dict['bid_vols']
        except (KeyError, ValueError):
            return [0] * 5

    @property
    def limit_up(self):
        """
        [float] 涨停价
        """
        try:
            return self._tick_dict['limit_up']
        except (KeyError, ValueError):
            return 0

    @property
    def limit_down(self):
        """
        [float] 跌停价
        """
        try:
            return self._tick_dict['limit_down']
        except (KeyError, ValueError):
            return 0

    @property
    def isnan(self):
        return np.isnan(self.last)

    def __repr__(self):
        items = []
        for name in dir(self):
            if name.startswith("_"):
                continue
            items.append((name, getattr(self, name)))
        return "Tick({0})".format(', '.join('{0}: {1}'.format(k, v) for k, v in items))

    def __getitem__(self, key):
        return getattr(self, key)
