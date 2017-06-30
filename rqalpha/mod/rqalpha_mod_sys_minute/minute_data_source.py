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

from rqalpha.data.base_data_source import BaseDataSource
from rqalpha.data.daybar_store import DayBarStore
from rqalpha.data.converter import StockBarConverter_mb
from rqalpha.data.converter import IndexBarConverter_mb

from rqalpha.model.snapshot import SnapshotObject
from rqalpha.utils.logger import system_log
from datetime import date


class MinuteDataSource(BaseDataSource):
    def __init__(self, env):
        path = env.config.base.data_bundle_path
        super(MinuteDataSource, self).__init__(path)