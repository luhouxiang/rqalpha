from rqalpha.api import *
import talib
import numpy as np
import pandas as pd


def init(context):
    scheduler.run_daily(set_stocks, time_rule='before_trading')

    context.stocks = []

    # 设置我们要操作的股票池
    # update_universe(context.stocks)
    context.s = '000001.XSHG'


def set_stocks(context, bar_dict):
    need_stocks_codes = all_instruments(type='CS')
    need_stocks_codes = list(need_stocks_codes['order_book_id'])
    need_stocks_codes = filter_paused_stock(need_stocks_codes)
    need_stocks_codes = filter_listed_date_stock(need_stocks_codes)
    '''
    need_stocks_codes=index_components('000002.XSHG')
    need_stocks_codes=filter_paused_stock(need_stocks_codes)
    need_stocks_codes=filter_listed_date_stock(need_stocks_codes)
    '''
    context.stocks = need_stocks_codes
    # logger.info('--->today stock pool_size:%d'% len(context.stocks))
    # logger.info(context.stocks)


# 过滤停牌股票
def filter_paused_stock(stock_list):
    return [stock for stock in stock_list if not is_suspended(stock)]


# 过滤上市不满60天的股票
def filter_listed_date_stock(stock_list):
    return [stock for stock in stock_list if instruments(stock).days_from_listed() > 60]

# 初始化此策略
def handle_bar(context, bar_dict):
    # 取得当前的现金
    # 循环股票列表
    for stock in context.stocks:
        cash = context.portfolio.cash
        # 获取股票的数据
        hhigh = history_bars(stock, 30, '1d', 'high')
        hlow = history_bars(stock, 30, '1d', 'low')
        hclose = history_bars(stock, 30, '1d', 'close')
        flag = True
        if cash < 50000:
            flag = False
        # 创建STOCH买卖信号，包括最高价，最低价，收盘价和快速线（一般取为9），慢速线
        # 注意：STOCH函数使用的price必须是narray
        k, d = talib.STOCH(hhigh,
                           hlow,
                           hclose,
                           fastk_period=9,
                           slowk_period=3,
                           slowk_matype=0,
                           slowd_period=3,
                           slowd_matype=0)

        # 获取可卖股数
        current_position = context.portfolio.positions[stock].quantity
        current_sellable = context.portfolio.positions[stock].sellable
        # 获取当前股票价格
        current_price = bar_dict[stock].close
        # 死叉卖出，且拥有的股票数量>0时，卖出所有股票
        if k[-1] < d[-1] and k[-2] > d[-2] and current_sellable > 0:
            if bar_dict[stock].last > bar_dict[stock].limit_down:
                logger.info('---死叉全部卖出%s' % stock)
                order_percent(stock, -1)
        # 金叉时且当前无持仓，买入一手，
        elif k[-1] > d[-1] and k[-2] < d[-2] and current_position == 0:
            if bar_dict[stock].last < bar_dict[stock].limit_up and flag:
                logger.info('--->金叉买入全部%s' % stock)
                order_percent(stock, 1)





