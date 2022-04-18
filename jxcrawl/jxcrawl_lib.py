#coding=utf-8

"""
作者：xjxfly
邮箱：xjxfly@qq.com

申明：
1. 这是爬虫包，调用本包中的接口，将直接从公开网站拿公开数据.

2. 本包作者不对数据的真实性，准确性，时效性等负责，本包接口返回的数据都是来自公开网站的公开数据。
	调用者调用本包接口返回数据用于决策、计算等等，引发的自身经济损失或法律问题由使用者自己承担，和本包作者无关。

3. 本包仅用于学习研究，禁止用来向各接口所指向的网站发起攻击或频繁调用使其不堪重负或瘫痪。
"""


# -----------------------------
# 定义可以暴露给外部的接口，必须放在 __all__ 中，且外部只有用 from import 引用时才有效，直接 import 的话，这里的 __all__ 不起作用。；
# 另外，python 内置函数 help() 调用包或模块时，如果模块或包内有 __all__，则只返回 __all__ 中列出的接口的使用方法；否则返回全部接口的使用方法。 
# 这句既是给 from import 看的，也是给内置函数 help() 看的

__all__ = [
	'get_api_list',
	
	'get_all_code',
	'get_all_code_df',
	#'get_data',
	'get_k_data',
	'get_live_data',
	'get_distribution',
	'get_fund_flow',
	'get_page',
	'get_table',
	'get_usa_live_data',
	
	'is_trade_date',
	'make_header',
	'save_page'
	]


# --------------------------------------
# from . import common_config as cf 			# 引入本包的配置文件
from jxcrawl import common_config as cf

import gevent
if cf.MONKEY_PATCH_ALL:
	from gevent import monkey
	monkey.patch_all()

import pandas as pd
import random
import time
import datetime
import math
import json
import re


# import pysnooper

#import requests 		# 好用的爬虫请求库，比下面的 urllib 好用
#import selenium 		# 用于浏览器自动化
import bs4 				# 用于解析 html 

from urllib.request import urlopen, Request
from selenium import webdriver 				# 用于浏览器自动化
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities 		# 用于构造浏览器请求头
from selenium.webdriver.chrome.options import Options


import jxbase as jxb 						# 引入自定义基础包
import cnstock 								# 引入中国股市规则包


#########=====================================================


# ------------------------------------------------
# ------------------------------------------------
# functions start here

# ---------------------------------
# public interface start

# 先从自定义中国股市规则包 cnstock 获取交易规则（以字典形式返回），因为本包中的行情接口数据会用到股市规则
# B 股规则及基金还没定义，但他们的类别代码已定义，可用于取行情数据
stock_default_rule_dict = cnstock.get_rule() 					# 获取中国股市默认交易规则

stock_60_rule_dict = cnstock.get_rule(code_type='sh60') 		# 获取中国股市沪市 60 开头股票交易规则
stock_688_rule_dict = cnstock.get_rule(code_type='sh688') 		# 获取中国股市沪市 688 开头科创板股票交易规则

stock_00_rule_dict = cnstock.get_rule(code_type='sz00') 		# 获取中国股市深市 00 开头股票交易规则
stock_30_rule_dict = cnstock.get_rule(code_type='sz30') 		# 获取中国股市深市 300 创业板股票交易规则



# -----------------------------------------------------------------

def get_api_list():
	"""
	功能说明：本函数仅仅用于返回可用接口列表，不在列表中列出的函数或接口等请不要调用，他们一般在内部实现使用，未来可能会改名或调整！！

	Returns
	-------
	返回值：可用接口, list形式

	"""
	return __all__








def get_all_code(wait_time=cf.WAIT_TIME, source='eastmoney'):
	"""
	功能说明：到指定的源去取所有股代码，默认到东财取所有股
	参数：
		wait_time : 数值型, 可选，默认值: 0.1秒。
			说明：该参数表示相邻两次调用间隔时间，若有必要，用户可以指定一个间隔时间，以防给服务器增加压力。
			但接口在访问有些源时可能不会理会这个参数。
		source : 字符串型, 可选，默认值： 'eastmoney'
			说明：这个参数指明数据源。可取以下值（不区分大小写）：
			'eastmoney': 表示东财
			注：目前暂时只支持这个源。
	返回值：list型, 元素为股票代码；如果没取到，则返回 None
	"""
	all_code_arr = None
	
	if source.upper() == 'EASTMONEY':
		all_code_df = get_all_code_df(wait_time=wait_time, source=source)
		if all_code_df is not None:
			all_code_arr = all_code_df.code.tolist()
		
	return all_code_arr







def get_all_code_df(wait_time=cf.WAIT_TIME, source='eastmoney'):
	"""
	功能说明：到指定的源去取所有股代码，默认到东财取所有股
	参数：
		wait_time : 数值型, 可选，默认值: 0.1秒。
			说明：该参数表示相邻两次调用间隔时间，若有必要，用户可以指定一个间隔时间，以防给服务器增加压力。
			但接口在访问有些源时可能不会理会这个参数。
		source : 字符串型, 可选，默认值： 'eastmoney'
			说明：这个参数指明数据源。可取以下值（不区分大小写）：
			'eastmoney': 表示东财
			注：目前暂时只支持这个源。
	返回值：list型, 元素为股票代码；如果没取到，则返回 None
	"""
	all_code_df = None
	
	if source.upper() == 'EASTMONEY':
		all_code_df = get_all_code_from_eastmoney(wait_time=wait_time)
		#all_code_arr = all_code_df.code.tolist()
		
	return all_code_df




'''
def get_data(
		code_arr=None,
		xtype='tick',
		realtime=True,
		index=False,
		k_level='d',
		xbegin=None,
		xend=None,
		source=None,
		category='stock',
		market='hushen',
		asyn=False,
		*args,
		**kwargs
		):
	"""
	功能说明：根据传入的证券代码数组，调用相应的数据接口爬取数据，以 df 形式返回，若没有相应的数据，则返回 None;
	参数：
		code_arr, list型，必填。
			说明：该参数为待取数据的证券代码列表，若是股票，每个元素需为6位字符串股票代码;
		xtype: str型，可选，默认值：'tick'
			说明：该参数表示取何种数据。可取以下值（不区分大小写）：
			'tick': 表示取 tick 数据；
			'k': 表示取 K 线数据。
		realtime: 布尔型，可选，默认值：True
			说明：该参数表示取实时数据还是历史数据，可取以下值：
			True: 表示取实时数据；
			False: 表示取历史数据。
		index: 布尔型，可选，默认值：False.
			说明：表明传入的 code_arr 其元素是否指数，可取以下值：
			True：表示取指数数据；
			False: 表示取普通证券数据。
		k_level: str型，可选，默认值 'd'
			说明：该参数表示取K线数据的级别，只有参数 xtype='k' 时，本参数才有效。可取以下值（不区分大小写）：
			'd': 表示取日K线
			'h': 表示取小时K线数据（暂不支持）
			'm': 表示取分钟K线数据（暂不支持）
		xbegin: str型或python日期型，可选，默认值 None
			说明：本参数表示取K线数据的开始日期，取值接受python日期格式或字符串格式，如datetime.date(2020,1,1) 或 '2020-01-01';
			xbegin 若不输入，则取今年第一天（即元旦）；
		xend: str型或python日期型，可选，默认值 None
			说明：表示取K 线数据的结束日期，取值类型同上;
			xend 若不输入，则取今天;
			注意：xbegin 和 xend，只有在参数 xtype='K' 时才起作用。
		source: str型，可选，默认值 None
			说明：该参数表示从哪个源获取，可取以下值（除None值外不区分大小写）：
			None：表示用户不指定源，由接口自己决定；
			'sina'：表示从新浪取数据；
			'netease'：表示从网易取数据；
			如果用户指定源，则从相应的源获取；
			如果用户不指定源，即为 None时，由接口自己从所有可能的源并发获取，哪个源先返回数据就用该数据，
			并立即终止其他源的数据获取。
			
		category: str型，可选，默认值：'stock'
			说明：该参数表示取哪种数据；可取以下值（不区分大小写）：
			'stock'：表示股票；
			'futures'：表示期货；
			'gold'：表示黄金；
			'exchange'：表示外汇；
			'bitcoin'：表示比特币；
			目前暂时只支持 stock(股票)。
		market: str型，可选，默认值 'hushen'
			说明：该参数表示获取哪个交易市场的数据。可取以下值（不区分大小写）:
			'hushen'：表示沪深市场；
			'usa': 表示美股市场；
			'dow'：表示道琼斯市场；
			'nasdaq'：表示纳斯达克。
			目前暂时只支持'hushen','usa'。
		asyn: bool型，可选，默认值：False
			说明：该参数用来指明本接口是通过异步方式调用还是同步方式调用，默认 False 表示同步方式，
			本参数可取以下值：
			True: 表示通过异步方式调用
			False: 表示通过同步方式调用。（建议用这个，防止异步方式给网站压力过大而被封IP）
		args 和 kwargs 为不定参数，预留。
	返回值：相应证券的数据，df 格式
	"""
	df = None 			# 预设返回值为 None	
	
	if market.upper() == 'HUSHEN' and code_arr is None:
		print('错误！你选择了沪深市场，请输入股票代码 list 给形参 code_arr')
		return None
	
	# ---------------------------------------------------------------------------------
	# 如果 source 为 None ，则从多源异步获取实时股票数据，一旦第一个源返回了数据，则立即终止其他源的获取并使用第一个源获取到的数据
	if market.upper() == 'HUSHEN' and category.upper() == 'STOCK' and xtype.upper() == 'TICK' and realtime and source is None:
		# 如果 source 为 None ，则从多源并发异步获取
		g_arr = [] 		# 定义一个 list，用于保存协程对象
		source_arr = ['sina','netease'] 		# 定义一个 list，用于指定实时数据源网站
		random.shuffle(source_arr) 				# 打乱 source_arr 中的源顺序
		
		if asyn:
			# 异步方式走这里
			for source in source_arr:
				g = gevent.spawn(get_realtime_stock_data_async, code_arr, index, source) 		# 对每个源的获取行情动作产生一个协程对象
				g_arr.append(g)
			# 下面这句 gevent.wait() 表示对 g_arr 中的所有协程对象进行并发执行，是个执行动作，他后面的代码将被阻塞，wait 的意思就是等待所有协程执行完成
			# 如果指定了 count，则只要执行完 count 个协程就不再阻塞了，count=1 表示只要有一个完成的话流程就往 gevent.wait() 这句后面的代码走，
			gevent.wait(g_arr, count=1)
			# 下面遍历已完运行完成的协程对象，提取返回值（即爬回的数据）
			for g in g_arr:
				if g.value is not None:
					df = g.value
				else:
					gevent.kill(g)
			#df = get_realtime_stock_data_async(code_arr=code_arr, index=index, source='sina')
		else:
			# 同步方式走这里
			for source in source_arr:
				df = get_realtime_stock_data_sync(code_arr=code_arr, index=index, source=source)
				if df is None:
					continue
				else:
					break
		
	# ---------------------------------------------------------------------------------	
	# 从指定源获取实时股票数据
	if market.upper() == 'HUSHEN' and  category.upper() == 'STOCK' and xtype.upper() == 'TICK' and realtime and source is not None:
		if asyn:
			# 从指定源异步获取数据
			df = get_realtime_stock_data_async(code_arr=code_arr, index=index, source=source)
		else:
			# 从指定源同步获取数据
			df = get_realtime_stock_data_sync(code_arr=code_arr, index=index, source=source)
			
			
			
	# ---------------------------------------------------------------------------------		
	# 从网易获取日K线数据	
	if market.upper() == 'HUSHEN' and  category.upper() == 'STOCK' and xtype.upper() == 'K':
		if source is None:
			source = 'netease'
		if xbegin is None:
			xbegin = datetime.date(jxb.get_year(),1,1) 		# 构造今年元旦
		if xend is None:
			xend = jxb.get_yesterday()			# 获取昨天
		
		for code in code_arr:
			k_df = get_k_stock_data(code=code, xbegin=xbegin, xend=xend, index=index, k_level=k_level, source=source)
			if k_df is not None:
				"""
				# --------------
				# 如果是指数，则对返回的数据指数代码加上市场前缀
				if index:
					prefixed_code = cnstock.get_prefixed_code(code,by='letter',index=index) 		# 本函数只对针单只股加前缀
					k_df.code = prefixed_code 		# 对于指数，用加前缀后的代码（例如：'sh000001'）去替换返回的数据中的6位代码
				# ------------	
				"""
				if df is None:
					df = k_df
				else:
					df = pd.concat([df,k_df])
		if df is not None:
			df = df.sort_values(by=['date'], ascending=[True])
			
	# ---------------------------------------------------------------------------------
	# 以下从新浪获取美股所有股票行情
	if market.upper() == 'USA' and category.upper() == 'STOCK' and xtype.upper() == 'TICK' and realtime:
		df = get_sina_realtime_usa_stock_data()
	
	# ------------------------------------
	# ---------------------
	# 将上面获取到的数据判断是否指数，若是的话，则将其代码加上市场前缀
	if index and df is not None:
		prefixed_code_arr = [cnstock.get_prefixed_code(x,by='letter',index=index) for x in code_arr]
		for i,code in enumerate(code_arr):
			# 将df的 code（这个code 表示列名） 列中数据内容用replace方法进行替换。 后面的 code变量（这个code 不是列名，而是code 列下的数据内容变量，把它所指的数据内容替换为 prefixed_code_arr[i] 所指的数据内容，inplace=True 表示直接替换
			df.code.replace(code, prefixed_code_arr[i], inplace=True)
	
	# ------------------------------------
	# ------------------------------------
	# 将 df 的行重新按自增整数编号
	if df is not None:
		df = df.reset_index(drop=True)
		
	return  df
'''







def get_k_data(code, xbegin, xend, index=False):
	"""
	功能说明：根据传入的股票代码和日期范围获取相应的K线数据，这和上面的 get_data(xtype='k') 是一样的。
	参数：
		code: 股票代码，str 型
		xbegin: 起始日期，str 型或python 日期型
		xend: 结束日期，str型或 python 日期型
	返回值：DF形式的K线数据
	"""
	k_df = get_k_stock_data(code=code, xbegin=xbegin, xend=xend, index=index)
	
	return k_df







def get_live_data(code_arr, index=False, source='tencent'):
	"""
	功能说明：根据传入的股票代码 list ，获取相应的实时数据返回
	参数：
		code_arr: 股票代码 list, 每个元素是str 型的股票代码
		index: 表示传入的 code_arr 是否指数，默认 False
		source: 表示从哪个源获取实时数据，可取值'sina','netease','qq'，不区分大小写
	返回值：df 形式的实时 tick 数据。

	"""
	df = get_realtime_stock_data_sync(code_arr=code_arr, index=index, source=source)
	
	return df







def get_distribution(code, xbegin, xend=None, category='stock', market='hushen'):
	"""
	功能说明：根据传入的股票代码和日期范围，获取筹码分布数据
	参数：
		code: str型，必填。
			说明：股票代码。
		xbegin: str型（格式 yyyy-mm-dd）或python 日期型，必填。
			说明：统计筹码分布的起始日期
		xend: str型（格式 yyyy-mm-dd）或python 日期型，可选，默认值: None。
			说明：统计筹码分布的结束日期，若没传入，则和 xbegin 取相同日期。
			表示 xbegin 这一天的筹码分布。
		category: str型，可选，默认值：'stock'
			说明：该参数表示取哪种数据；可取以下值（不区分大小写）：
			'stock'：表示股票；
			'futures'：表示期货；
			'gold'：表示黄金；
			'exchange'：表示外汇；
			'bitcoin'：表示比特币；
			目前暂时只支持 stock(股票)。
		market: str型，可选，默认值 'hushen'
			说明：该参数表示获取哪个交易市场的数据。可取以下值（不区分大小写）:
			'hushen'：表示沪深市场；
			'usa': 表示美股市场；
			'dow'：表示道琼斯市场；
			'nasdaq'：表示纳斯达克。
			目前暂时只支持'hushen'。
	返回值：	筹码分布数据（df 格式）
	"""
	table_arr = None
	if market.upper() == 'HUSHEN' and category.upper() == 'STOCK':
		table_arr = get_stock_price_volume_distribution(code=code, xbegin=xbegin, xend=xend)	

	return table_arr
	
	
	
	


	
	

def get_fund_flow(code, index=False, source='tencent', catetory='stock', market='hushen'):
	"""
	功能说明：从指定源获取指定证券的主力和散户资金流向
	参数：
		code: str型，必填。
			说明：需要获取资金流的证券代码; 
			注：暂时只支持沪深股票代码。
		index: bool 型，可选，默认值：False
			说明：该参数表示传入的 code 是否指数。可取以下值：
			True: 表示传入的 code 为指数代码；
			False: 表示传入的code 为普通证券代码。
		source: str 型，可选，默认值：'tencent'
			说明：该参数表示从哪个源获取数据，可取以下值（不区分大小写）：
			'tencent': 表示腾讯
			'qq': 同上
		category: str型，可选，默认值：'stock'
			说明：该参数表示哪种交易口种，可取以下值（不区分大小写）：
			'stock': 股票
			注：目前暂时只支持股票
		market: str型，可选，默认值：'hushen'
			说明：该参数表示从哪个市场获取数据，可取以下值（不区分大小写）：
			'hushen': 表示沪深市场
	返回值：资金流向数据（df 格式），若没取到则返回 None
	"""
	df = None
	if market.upper() == 'HUSHEN' and catetory.upper() == 'STOCK' and source.upper() in ['TENCENT','QQ']:
		df = get_stock_fund_flow(code=code, index=index, source=source)
		
	return df








def get_page(url_arr, asyn=False, by='requests', xcount=None):
	"""
	功能说明：请求 url_arr（list型） 指向的网页源码；请求方式由 by 指定。
	参数：
		url_arr : list型，必填。
			说明：该参数用来存放待请求的 url 的容器,可以一次传入 n 个 url 给 url_arr。
		asyn: bool型，可选，默认值：False
			说明：该参数用来指明本接口是通过异步方式调用还是同步方式调用，默认 False 表示同步方式，
			本参数可取以下值：
			True: 表示通过异步方式调用
			False: 表示通过同步方式调用。（建议用这个，防止异步方式给网站压力过大而被封IP）
		by : str型，可选，默认值：'requests'
			说明：该参数表示用什么包做请求，可取以下值（不区分大小写）：
			'gevent': 表示通过 gevent （异步）来请求页面；
			'urllib': 表示通过 urllib 这个库来请求 url_arr
			'requests': 表示通过 requests 这个库来请求 url_arr; requests（同步） 是默认方式
			'browser': 表示通过 browser （模拟浏览器）来请求，一般不要用这种方式，因为效率较低，除非上面的几种方式拿不到数据。
		xcount: int型或 None, 可选，默认值 None
			说明：该参数表示  url_arr 中只要有 xcount 个完成了就立即返回，其他的 url 不再请求，默认 None ，表示请求所有。
			xcount = 0 或取值超过 url_arr 元素个数时，都表示请求所有。
			注意：xcount 参数只有在 by='gevent' 时才发挥作用。	
	返回值：
		page_source_arr : list型, 每个元素是url_arr 中相应 url 的页面源码，若没取到则返回 None
	"""
	if not isinstance(url_arr, list):
		print("错误！ 请将各个待请求 url 放入到 list 中传给形参 url_arr")
		return None
	
	page_source_arr = [] 		# 返回的页面全部保存到这个 list ，并由本接口将其 return 给上层调用
			
	# get_page_by_gevent() 是异步请求方式，
	if by.upper() == 'GEVENT' or asyn:
		page_source_arr = get_page_by_gevent(url_arr=url_arr, xcount=xcount) 	
		
	# 下面3个都是同步请求方式。
	if by.upper() == 'REQUESTS':
		for url in url_arr:
			page_source = get_page_by_requests(url=url)
			page_source_arr.append(page_source)
			
	if by.upper() == 'URLLIB':
		for url in url_arr:
			page_source = get_page_by_urllib(url=url)
			page_source_arr.append(page_source)
			
	# 下面这个是模拟浏览器请求方式			
	if by.upper() == 'BROWSER':
		for url in url_arr:
			page_source = get_page_by_browser(url=url)
			page_source_arr.append(page_source)
			
	return page_source_arr
		







def get_table(page_source, separator='||'):
	"""
	功能说明：从网页源码中提取表格数据返回
	参数：
		page_source: str型，必填。
		说明：该参数要指向网页源码（可以是通过 requests 或 selenium + phantomjs等爬到的网页源码）；
		注意：页面源码必须是已经 decode() 过的纯文本（字符串形式），不能是字节流形式；
	返回值：table_arr, list型, 其中每个元素是对应网页中一个 <table> (df格式)。若页面不是 str型则返回 None
	"""
	if not isinstance(page_source, str):
		print('错误！请传入目标网页源码给参数 page_source（且必须已经 decode 成纯文本格式）')
		return None
	
	if separator is None:
		# 不建议用 ',' 做数据之间分割符，因为实践中发现，有的爬回的数值型数据每3位有一个逗号，
		# 若此处用逗号做分割的话，数值将被拆散成多列，完全不符合要求。
		# separator = ',' 		
		separator = '||'
	# -----------------------
	# 在转成 soup 前把源码中的一些转后可能出问题的字符替换掉
	page_source = page_source.replace('&nbsp;','') 				# 页面源码中的 &nbsp; （对应网页上的空格）在转成 soup 后会变成 \xa0，使得 soup 后的 get_text() 操作会出错。所以先去掉 &nbsp; ，防止转 soup 后出现 \xa0
	#soup = bs4.BeautifulSoup(page_source, "html5lib") 			# 准备用 lxml 解析网页源码内容 page_source。注意：即便装了 html5lib 模块，在执行这句时也有问题，好像会卡死。
	soup = bs4.BeautifulSoup(page_source, "lxml") 				# 准备用 lxml 解析网页源码内容 page_source. 注意：这里的 page_source 必须是纯文本的字符串，也就是要已经 decode() 过了的

	table_arr = [] 		# 用于存放网页上的一个个表格，这个 list 的元素对应网页上的一个 <table>
	tables = soup.find_all('table') 		# 返回 soup （页面源码）中的所有 table
	for table in tables:
		trs = table.find_all('tr')
		temp_table = [] 			# 每一个temp_table ,用于保存网页上的一个 table数据，以二维 list 保存
		for tr in trs:
			row_str = tr.get_text(separator=separator)
			row_arr = row_str.split(separator)
			temp_table.append(row_arr)

		if len(temp_table) > 0:
			temp_table = pd.DataFrame(temp_table) 			# 将二维 list 转成 DataFrame
			table_arr.append(temp_table)

	return table_arr








def get_usa_live_data():
	"""
	说明：从新浪获取美股实时行情
	参数：无
	返回值：美股所有股行情，df格式
	"""
	df = get_sina_realtime_usa_stock_data()

	return df







def is_trade_date(category='stock', market='hushen'):
	"""
	功能说明：判断今天是否交易日。该函数通过从获取指数（上证综指）的实时数据中提取日期，以判断今天是否交易日。
		注意：只有在开盘后调用才有用，所以建议在 9：15 后调用本函数，否则不准。
	参数：无 
	返回值：bool型，交易日返回 True, 非交易日返回 False. 无法判断返回 None.
	"""
	func_name = jxb.get_current_function_name() + ': '
	df = None
	xtoday = jxb.get_today()
	
	if category.upper() == 'STOCK' and market.upper() == 'HUSHEN':
		if time.time() <= jxb.hms_to_timestamp(xtime=stock_default_rule_dict['OPEN_TIME']):
			print(jxb.get_current_time(),func_name,' 本函数是针对实盘判断是否交易日的，请在 %s 开盘后调用。' % (stock_default_rule_dict['OPEN_TIME']))
			return False
		# shzz = '000001' 			# 这句也是正确的，但为了便于维护，采用下面这一句，让所有地方的指数都从 cnstock 这个包获取
		shzz = cnstock.get_index_code() 			# 获取上证综指代码（不加参数默认就是返回上证综指代码）
		df = get_live_data(code_arr=[shzz], index=True)
	
	if df is None:
		return False
	
	if str(df.loc[0,'date']) == str(xtoday):
		return True
	else:
		return False








def make_header():
	"""
	功能说明：构造一个 http 请求头返回
	"""
	header = jxb.make_header()
	return header







def save_page(page_source, filename, mode='a'):
	"""
	功能说明：把抓下来的网页源码以utf-8 编码保存到文件
	参数：
		page_source: str型，必填。
			说明：该参数要指向已经 decode 的网页源码； 
		filename: str型，必填。
			说明：该参数表示文件名（可以是包含驱动盘符及目录的全路径），用于保存页面源码; 
		mode: str型，可选，默认值：'a'
			说明：该参数表示打开文件模式（是读，是新建，还是追加内容的写等），此处默认追加方式。
			具体取值参见 python 的 open() 函数。
	返回值：无
	"""
	try:
		f = open(filename, mode, encoding='utf-8')
		f.write(page_source)
		f.close()
	except:
		print("错误！保存文件出错。")








def z():
	"""
	功能说明：这个函数没有实际功能，仅仅是表明上面的公开接口到此为止，下面的函数都是内部私有函数。

	Returns
	-------
	None.

	"""
	print('这个函数没有实际功能，仅仅是表明上面的公开接口到此为止，下面的函数都是内部私有函数。')
	pass








# public interface end
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
# ======================================================================================================














# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
# ======================================================================================================

# ----------------------------------
# ----------------------------------
# ----------------------------------
# ----------------------------------
# ----------------------------------
# ----------------------------------
# ----------------------------------
# ----------------------------------
# private interface for inner use start


def get_page_by_urllib(url, header=None):
	"""
	说明：下载（获取）指定 URL 的页面源码。
	参数：url：目标地址; headers: 请求头，若没有传入，则由本函数自己调用请求头。
	返回值：url 指向的 page_source（本函数已经将取到的 page_source  decode() 成字符串形式（纯文本））
	"""
	if header is None:
		header = make_header()
	req = Request(url, headers=header)
	opener = urlopen(req)
	# charset = opener.info().get_content_charset() 		# 这句和下面这句是一样的，只需用一句即可
	charset = opener.headers.get_content_charset() 			# 从返回的字节流中提取字符编码方式，待会后面要用到
	if charset is not None:
		page_source = opener.read().decode(charset) 		# 用上一句读取到的编码方式不是 None ，则用它进行解码
	else:
		page_source = opener.read().decode() 				# 若 charset 为 None，则用不带参数的 decode() 解码

	return page_source  	









def get_page_by_requests(url, header=None):
	"""
	说明：下载（获取）指定 URL 的页面源码。对于静态 html 或网站能直接提供数据的（包括api形式，string 形式，json形式等），
		若网站的数据没有直接给，而是用 js 方式提供的话，则请调用下面的 get_page_by_browser() 方式去获取，它是模拟浏览器的
	参数：url：目标地址; headers: 请求头，若没有传入，则由本函数自己调用请求头。
	返回值：url 指向的 page_source（本函数已经将取到的 page_source  decode() 成字符串形式（纯文本））
	"""
	page_source = jxb.get_page_by_requests(url=url, header=header)

	return page_source







def get_page_by_gevent(url_arr, xcount=None):
	"""
	功能说明：调用该函数返回网页 url_arr 所指向的一堆网页的源码。
	Parameters
	----------
	url_arr : list
		是 url list，每个元素是一个 url
	xcount : int
		取值正整数或 None，表示url_arr 中完成几个即结束；默认值None ，表示需要完成所有 url 的请求

	Returns
	-------
	是一个 list ，每个元素是 url_arr 中相应 url 的 page_source
	"""	
	# 以下这两句都是正确的，两个函数 get_page_by_gevent 的代码是一模一样的，
	# 只是一个放到 jxbase 包中， 一个放在本包下。原来只要调用 jxbase 中的 get_page_by_gevent 就可以了，
	# 但为了方便本爬虫包用户通过本包配置文件控制是否要启用 monkey.patch_all() ，而 patch_all() 又要求在所有其他 import 之前之行
	# 所以只好把 jxbase 中的 get_page_by_gevent() 复制一个到本包来了。
	#page_source_arr = jxb.get_page_by_gevent(url_arr=url_arr, xcount=xcount)
	page_source_arr = get_page_by_gevent_0(url_arr=url_arr, xcount=xcount)
	
	return page_source_arr






def get_page_by_gevent_0(url_arr, xcount=None):
	"""
	功能说明：调用该函数返回由url_arr 所指向的一堆url所对应的页面源码。
	Parameters
	----------
	url_arr : list
		是 url list，每个元素是一个 url
	xcount : int
		取值正整数或 None，表示url_arr 中完成几个即结束；默认值None ，表示需要完成所有 url 的请求

	Returns
	-------
	是一个 list ，每个元素是 url_arr 中相应 url 的 page_source
	"""
	if xcount is None or xcount <= 0 or xcount > len(url_arr):
		xcount = len(url_arr)
		
	g_arr = [] 		# 存放协程对象
	for url in url_arr:
		g = gevent.spawn(get_page_by_requests, url)
		g_arr.append(g)
	# gevent.wait() 执行 g_arr 中的各个协程对象，count = 1 表示g_arr 中的协程对象只要有一个完成了就立马返回主线程往下走，
	# 即执行 gevent.wait() 后面的代码，而不再等其他几个一起完成才返回主线程
	gevent.wait(g_arr, count=xcount)
	# 下面这个 for , 从上面返回的协程中提取 value.
	page_source_arr = []
	for g in g_arr:
		if g.value is None:
			continue
		else:
			page_source = g.value
			page_source_arr.append(page_source)
		
	return page_source_arr







def get_page_by_browser(url, browser=None):
	"""
	说明：通过浏览器下载（获取）指定 URL 的页面源码）
	参数：url：目标网页地址; browser: 指定浏览器driver的程序名，可以是包含驱动器的全路径
	返回值： 页面源码 page_source（已经是纯文本形式（即字符串），无需再调用 decode() 解码，要不然要出错）
	"""
	browser_driver = get_browser_driver(browser=browser)
	if browser_driver is None:
		return None

	browser_driver.get(url)
	page_source = browser_driver.page_source

	return page_source





def get_prefixed_code_arr(code_arr, by='letter', index=False):
	"""
	说明：该函数对传入的股票代码数组 code_arr 中的每一只股加上市场代码前缀（如'sh'或'0' ）后，以数组形式返回
	参数：code_arr: 待加前缀的6位股票代码（字符串形式）构成的数组； by: 取值'letter' 或 'number'，表示加字母前缀（'sh','sz' 等）还是加数字前缀（'0','1'等）
		index: 表示传入的 code_arr 中的股票代码是否指数，取值 True 或 False
	返回值：加了前缀后的股票代码数组
	"""	
	prefixed_code_arr = []

	for i,code in enumerate(code_arr):
		prefixed_code = None
		# 调用 cnstock 包的 get_prefixed_code() 对股票代码加上市前缀（该函数会自动判断股票代码属于哪个市场）
		prefixed_code = cnstock.get_prefixed_code(code=code, by=by, index=index)
		if prefixed_code is not None:
			prefixed_code_arr.append(prefixed_code)

	return prefixed_code_arr










def get_browser_driver(browser=None):
	"""
	说明：根据传入的浏览器（路径）调用相应的接口来返回该浏览器的 browser_driver
	参数：browser: 浏览器程序（可以含全路径）
	返回值：和浏览器相对应的 selenium 下的 webdriver调用该浏览器形成的 browser_driver返回。
	"""
	func_name = jxb.get_current_function_name()
	browser_driver = None
	if browser is None:
		# 如果用户没有指定浏览器，则首先 Phantomjs 
		try:
			browser_driver = get_phantomjs_browser_driver()
		except:
			print(func_name,' 调用 phantomjs 浏览器失败！')
		else:
			return browser_driver

		try:
			browser_driver = get_chrome_browser_driver()
		except:
			print(func_name,' 调用 chrome 浏览器失败！')
		else:
			return browser_driver
	else:
		if browser.upper().find('PHANTOMJS') >= 0:
			try:
				browser_driver = get_phantomjs_browser_driver(browser=browser)
			except:
				print(func_name,' 调用 phantomjs 浏览器失败！')
			else:
				return browser_driver

		if browser.upper().find('CHROME') >= 0:
			try:
				browser_driver = get_chrome_browser_driver(browser=browser)
			except:
				print(func_name,' 调用 chrome 浏览器失败！')
			else:
				return browser_driver

	return browser_driver






def get_phantomjs_browser_driver(browser=None):
	"""
	功能说明：根据传入的浏览器驱动（可以全路径文件名）程序，返回一个 selenium 处理后的 webdriver，用于浏览器自动化
	若用户没有 phantomjs.exe 浏览器驱动，可到以下链接下载（下载后将 phantomjs.exe 解压出来放到 path 所指的一条路径即可）：
	https://phantomjs.org/download.html
	https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-windows.zip
	"""
	if browser is None:
		if jxb.is_windows():
			browser = "phantomjs.exe"
			dcap = dict(DesiredCapabilities.PHANTOMJS)
		if jxb.is_linux():
			browser = "phantomjs"
			dcap = {} 

	browser_driver = None
	header = make_header()
	dcap = dict(**dcap, **header) 		# 构造请求头
	#browser_driver = webdriver.PhantomJS(browser, service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any']) 
	try:	
		browser_driver = webdriver.PhantomJS(browser, desired_capabilities=dcap)
	except:
		print("错误！没检测到 PhantomJS 浏览器。如果还没安装可到以下网址下载安装。")
		print("如果已经安装，请将 phantomjs.exe 所在路径添加到系统 path 中。")
		print("phantomjs 下载地址（请自备梯子）：")
		print("	https://phantomjs.org/download.html")
		print("	https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-windows.zip")
	
	return browser_driver






def get_chrome_browser_driver(browser=None):
	"""
	功能说明：根据传入的浏览器驱动（可以全路径文件名）程序，返回一个 selenium 处理后的 webdriver，用于浏览器自动化
	若用户没有 chromedriver.exe 浏览器驱动，可到以下链接下载（下载后将 chromedriver.exe 解压出来放到 path 所指的一条路径即可）：
	https://chromedriver.chromium.org/
	https://chromedriver.storage.googleapis.com/index.html?path=88.0.4324.96/
	"""
	if browser is None:
		if jxb.is_windows():
			browser = "chromedriver.exe"
			#dcap = dict(DesiredCapabilities.CHROME)
		if jxb.is_linux() :
			browser = "chromedriver"
			#dcap = {} 

	browser_driver = None
	#header = make_header()
	#dcap = dict(**dcap, **header) 		# 构造请求头
	#browser_driver = webdriver.PhantomJS(browser, service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any']) 
	try:
		chrome_options = Options()
		chrome_options.add_argument('--headless')
		chrome_options.add_argument('--disable-gpu')		
		browser_driver = webdriver.Chrome(executable_path=browser, chrome_options=chrome_options)
	except:
		print("错误！没检测到 chrome 浏览器驱动。请先下载安装。")
		print("如果已经安装，请将 chromedriver.exe 所在路径添加到系统 path 中。")
		print("ChromeDriver 下载地址（请自备梯子）：")
		print("https://chromedriver.chromium.org/")
		print("https://chromedriver.storage.googleapis.com/index.html?path=88.0.4324.96/")

	return browser_driver









# ---------------------------------
# sina data start

def get_realtime_stock_data_async(code_arr, index=False, source='tencent'):
	"""
	说明：根据传入的股票代码数组，用异步方式获取实时数据，以 df 形式返回
	参数：code_arr, 待取实时数据的股票代码列表，index 表明是否指数
	返回值：相应股票的实时数据，df 格式
	"""
	xcount = None
	if source.upper() == 'SINA':
		package_size = 800 			# 一次拿几只股的实时数据 (新浪一次性最大支持 800只)
	if source.upper() == 'NETEASE':
		package_size = 1000 		# 一次拿几只股的实时数据 (网易一次性最大支持 1000只)
	if source.upper() in ['TENCENT','QQ']:
		package_size = 900			# 一次拿几只股的实时数据 (腾讯一次性最大支持 900只)
	
	xcount = math.ceil((len(code_arr) / package_size)) 			# 共需几组才能拿完
	if xcount is None:
		return None
	
	url_arr = [] 				# url list
	all_df = None 				# all_df 用来保存新浪返回的实时行情数据，预设 None
	for i in range(xcount):
		temp_arr = code_arr[i*package_size:(i+1)*package_size]
		if source.upper() == 'SINA':
			url = get_sina_realtime_stock_url(code_arr=temp_arr, index=index) 			# 把股票 list 串接成符合新浪数据源要求的格式返回
		if source.upper() == 'NETEASE':
			url = get_netease_realtime_stock_url(code_arr=temp_arr, index=index) 		# 把股票 list 串接成符合网易数据源要求的格式返回
		if source.upper() in ['TENCENT','QQ']:
			url = get_tencent_realtime_stock_url(code_arr=temp_arr, index=index) 		# 把股票 list 串接成符合腾讯数据源要求的格式返回
		url_arr.append(url)

	# page_source_arr = get_page_by_gevent(url_arr=url_arr)
	# asyn=True 和 by = 'gevent'都表示用异步方式请求,两者只要选用一个就行，两个都用也没关系。
	page_source_arr = get_page(url_arr=url_arr, asyn=True, by='gevent') 		
	if page_source_arr is None:
		return None
	
	all_df = None
	for page_source in page_source_arr:
		df = None
		if source.upper() == 'SINA':
			df = get_sina_realtime_stock_data_from_page_source(page_source=page_source)
		if source.upper() == 'NETEASE':
			df = get_netease_realtime_stock_data_from_page_source(page_source=page_source)
		if source.upper() in ['TENCENT','QQ']:
			df = get_tencent_realtime_stock_data_from_page_source(page_source=page_source)
		if df is None:
			continue
		
		if all_df is None:
			all_df = df
		else:
			all_df = pd.concat([all_df,df])

	if all_df is not None:
		if (not index) and  is_trade_date()  and jxb.hms_to_timestamp(xtime=stock_default_rule_dict['OPEN_TIME']) <= time.time() <= jxb.hms_to_timestamp(xtime=stock_default_rule_dict['OPEN_PRICE_TIME']):
			all_df['open'] = all_df['bid1_price'] 			
			all_df['high'] = all_df['bid1_price']
			all_df['low'] = all_df['bid1_price']
			all_df['price'] = all_df['bid1_price'] 	
		
		all_df = all_df.reset_index(drop=True) 		# 由于 pd.concat() 会拼接重复索引，所以这里要 reset_index() 一下，drop=True 表示删除原来的索引 

	return all_df








def get_realtime_stock_data_sync(code_arr, index=False, source='tencent'):
	"""
	说明：根据传入的股票代码数组，用同步方式到新浪获取实时数据，以 df 形式返回，这个函数只是起一个分层作用，往下调用 get_realtime_stock_data_sync_0()
	参数：code_arr, 待取实时数据的股票代码列表，index 表明是否指数
	返回值：相应股票的实时数据，df 格式
	"""
	package_size = None
	if source.upper() == 'SINA':
		package_size = 800 				# 一次拿几只股的实时数据 (新浪一次性最大支持 800只)
	if source.upper() == 'NETEASE':
		package_size = 1000 			# 一次拿几只股的实时数据 (网易一次性最大支持 1000只)
	if source.upper() in ['TENCENT','QQ']:
		package_size = 900 				# 一次拿几只股的实时数据 (腾讯一次性最大支持 900只)
	
	if package_size is None:
		return None
	
	xcount = math.ceil((len(code_arr) / package_size)) 			# 共需几组才能拿完

	all_df = None 				# all_df 用来保存新浪返回的实时行情数据，预设 None
	for i in range(xcount):
		df = get_realtime_stock_data_sync_0(code_arr=code_arr[i*package_size:(i+1)*package_size], index=index, source=source) 			# 新浪允许的最大包为 800 只左右，超过这个值将出错
		if df is None:
			continue
		else:
			if all_df is None:
				all_df = df
			else:
				all_df = pd.concat([all_df,df])

	if all_df is not None:
		all_df = all_df.reset_index(drop=True) 		# 由于 pd.concat() 会拼接重复索引，所以这里要 reset_index() 一下，drop=True 表示删除原来的索引 

	return all_df








def get_realtime_stock_data_sync_0(code_arr, index=False, source='tencent'):
	"""
	说明：根据传入的参数，构造相应的URL，到相应的源请求数据。
	"""
	func_name = jxb.get_current_function_name() + ': '
	url = None
	if source.upper() == 'SINA':
		url = get_sina_realtime_stock_url(code_arr=code_arr, index=index) 					# 把股票 list 串接成符合新浪数据源要求的格式返回
	if source.upper() == 'NETEASE':
		url = get_netease_realtime_stock_url(code_arr=code_arr, index=index) 				# 把股票 list 串接成符合网易数据源要求的格式返回
	if source.upper() in ['TENCENT','QQ']:
		url = get_tencent_realtime_stock_url(code_arr=code_arr, index=index) 				# 把股票 list 串接成符合腾讯数据源要求的格式返回
	
	if url is None:
		return None
	
	retry_count = 20 			# 拉取数据最多尝试次数
	xcount = 1
	page_source = None
	while True:
		if xcount > retry_count:
			print(func_name,'错误：拉取数据失败。')
			return None
		try:
			#page_source = urlopen(xrequest, timeout=10).read() 		# 提交请求并读取返回的网页源码
			#page_source = page_source.decode('GBK') 	# 新浪情行返回的数据流要用 GBK 解码
			#page_source = get_page_by_requests(url=url) 		# 这个 url 返回的数据已经解码（即已经 decode() 过了）			
			page_source_arr = get_page([url])
			if page_source_arr is not None:
				page_source = page_source_arr[0]
		except:
			s = random.randint(1,5)			
			print(func_name,'\n由于发生了错误，或 %s 行情服务器未能返回数据，本接口休息 %d 秒后将自动重新尝试拉数据。已尝试 %d / %d 次' % (source, s, xcount, retry_count))			
			time.sleep(s) 			# 如果被服务器踢，则停止3秒再拉数据
			xcount += 1
			continue
		else:
			if page_source is None:
				xcount += 1
				continue
			else:
				break
	
	df = None
	if source.upper() == 'SINA':
		df = get_sina_realtime_stock_data_from_page_source(page_source=page_source) 	# 解析 page_source 源码，提取行情数据
	if source.upper() == 'NETEASE':
		df = get_netease_realtime_stock_data_from_page_source(page_source=page_source) 	# 解析 page_source 源码，提取行情数据
	if source.upper() in ['TENCENT','QQ']:
		df = get_tencent_realtime_stock_data_from_page_source(page_source=page_source) 	# 解析 page_source 源码，提取行情数据
	if df is None:
		return None
	# ------------------------------------------------------
	# 获取市价。这个细节处理要注意，因为 9：25前返回的数据里没有 price, open, high, low ，但有 bid1 价格，就用 bid1填充他们
	# 所以判断当前时间，若已过了 9：25 ，则用 price 本身做市价，否则用 bid1 做市价
	if (not index) and  is_trade_date()  and jxb.hms_to_timestamp(xtime=stock_default_rule_dict['OPEN_TIME']) <= time.time() <= jxb.hms_to_timestamp(xtime=stock_default_rule_dict['OPEN_PRICE_TIME']):
		df['open'] = df['bid1_price'] 			
		df['high'] = df['bid1_price']
		df['low'] = df['bid1_price']
		df['price'] = df['bid1_price'] 	

	return df







def get_sina_realtime_stock_url(code_arr, index=False):
	"""
	说明：该函数根据传入的股票代码数组，生成新浪实时股票行情的网址返回
	参数：code_arr: 股票代码列表；index： 表示code_arr 里的股票代码是否表示指数
	返回值：指向新浪实时行情的网址。
	"""
	if code_arr is None or len(code_arr)==0:
		print(jxb.get_current_function_name() + ': 错误！传入的股票代码列表 code_arr 不能为空。')
		return None

	base_url = 'http://hq.sinajs.cn/list=%s' 			# 选择 sina 实时数据源

	prefixed_code_arr = get_prefixed_code_arr(code_arr=code_arr, index=index) 	# 对股票代码数组中的每一只股加上市场代码前缀后返回，仍然是数组形式
	prefixed_code_str = ','.join(prefixed_code_arr)
	prefixed_code_str += ','
	url = base_url % (prefixed_code_str) 		# 将实际值（即 % 后面括号里的值）代入到 base_url 中去

	return url











def get_sina_realtime_stock_data_from_page_source(page_source):
	"""
	说明：根据传入的股票代码数组，到新浪获取实时数据，以 df 形式返回，根据经验最好一次性不超过 800 只
	参数：code_arr, 待取实时数据的股票代码列表，index 表明是否指数
	返回值：df, 相应股票的实时数据，df 格式
	"""
	if page_source is None:
		return None

	func_name = jxb.get_current_function_name()
	# 构造新浪股票实时行情列头名称，由于新浪返回的数据是没有 key 的，即是纯数据，而不是 dict 方式，所以他返回的数据是有顺序，
	# 所以这里给他配的列头不要更改顺序！				  
	column_arr = [
		'name', 		# 名称
		'code', 		# 代码
		'open', 		# 开盘价（元）
		'last_close', 	# 昨收价（元）
		'price', 		# 市价（元）
		'high', 		# 最高价（元）
		'low', 			# 最低价（元）

		'volume', 		# 成交量（股）
		'amount', 		# 成交额（元）

		'bid1_volume', 	# 买一量（股）
		'bid1_price', 	# 买一价（元）
		'bid2_volume', 	# 买二量（股）
		'bid2_price', 	# 买二价（元）
		'bid3_volume', 	# 买三量（股）
		'bid3_price', 	# 买三价（元）
		'bid4_volume', 	# 买四量（股）
		'bid4_price', 	# 买四价（元）
		'bid5_volume', 	# 买五量（股）
		'bid5_price', 	# 买五价（元）

		'ask1_volume', 	# 卖一量（股）
		'ask1_price', 	# 卖一价（元）
		'ask2_volume', 	# 卖二量（股）
		'ask2_price', 	# 卖二价（元）
		'ask3_volume', 	# 卖三量（股）
		'ask3_price', 	# 卖三价（元）
		'ask4_volume', 	# 卖四量（股）
		'ask4_price', 	# 卖四价（元）
		'ask5_volume', 	# 卖五量（股）
		'ask5_price', 	# 卖五价（元）

		'date', 		# 日期
		'time' 			# 时间
		]

	#xrequest = Request(url) 		# 构造请求格式

	# 设几个初始变量
	data_arr = [] 		# 存放新浪返回的行情数据 
	#df = None 			# 存放将上述行情数据转成 dataframe 格式后的数据
	
	# 流程进到这里表示拿到了行情数据，下面对数据进行提取和规范，形成 df 返回
	arr = page_source.split(';')
	for code_str in arr:
		arr2 = code_str.split('"')
		try:
			code = arr2[0][-7:-1] 		# 提取股票代码
			arr2 = arr2[1].split(',')	# 这里是行情各字段数据内容				
		except:
			continue
		
		if arr2[-1] == '':
			arr2 = arr2[0:-1]
		arr2.insert(1,code) 			# 将股票代码插在第2个元素位置，（第一个为股票名称）
		arr2 = arr2[0:7] + arr2[9:] 	# 将返回的数据去掉重复部分，以适配上面构造的列名称
		if len(arr2) > len(column_arr):
			arr2 = arr2[:len(column_arr)]
		data_arr.append(arr2)

	df = pd.DataFrame(data=data_arr, columns=column_arr) 			# 构造 DF， 并配上列头
	if len(df) == 0:
		print(func_name,' 错误！没有数据。')
		return None

	"""
	# 上面得到 df 后，把没有用的一些列去掉，即 temp开头的
	for i,col in enumerate(column_arr):
		if col.startswith('temp') :
			df.pop(col)
	"""
	# 股票代码要转成字符串，并补足前导0，所以这里要将其转成字符串，并调用字符串的方法右对齐左侧补数个 char 直到有 width 个: rjust(width,char)
	df['code'] = df['code'].astype(dtype=str).str.rjust(6,'0') 					

	# --------------------------------------------
	# 这些数值列转成 float
	float_column_arr = ['last_close','open','high','low','price','amount','bid1_price','bid2_price','bid3_price','bid4_price','bid5_price','ask1_price','ask2_price','ask3_price','ask4_price','ask5_price']
	df = jxb.convert_df_type(df=df, xtype=float, column_arr=float_column_arr)
	# 这些数值列转成 int
	int_column_arr =  ['volume','bid1_volume','bid2_volume','bid3_volume','bid4_volume','bid5_volume','ask1_volume','ask2_volume','ask3_volume','ask4_volume','ask5_volume']
	df = jxb.convert_df_type(df=df, xtype=int, column_arr=int_column_arr)
	# 由于新浪数据没有涨跌额及涨幅，所以取到新浪行情数据后计算出并加上这两项
	df['price_change'] = df['price'] - df['last_close'] 				# 计算出涨跌额
	df['percent'] = df['price_change'] / df['last_close'] 			# 计算出涨跌幅
	# 调整  df 中的列顺序，使之按 STOCK_COLUMN_ORDER_ARR 中的顺序排列
	df = jxb.sort_df_column(df=df, column_arr=cf.STOCK_COLUMN_ORDER_ARR)
	# ==========================
	# df = df.sort_values(by=['code'],ascending=[True]) 		# 这里不要按股票代码排序，用户传进来是什么顺序就保持他的顺序。
	df = df.reset_index(drop=True)

	return df









def get_sina_realtime_usa_stock_data():
	"""
	说明：从新浪获取美股实时行情
	参数：无
	返回值：美股所有股行情，df格式
	"""
	column_dict = {
		'name':'name', 			# 公司名称
		'cname':'cname', 		# 公司名称（中文）
		'category':'industry', 	# 行业
		'symbol':'code', 		# 股票代码。美股的代码是字母组合，A股代码是 6 位数字组合
		'price':'price', 		# 市价
		'diff':'price_change', 		# 涨跌额（美元）
		'chg':'percent', 		# 涨幅（用小数表示真实涨幅，例：0.02 就表示涨2%）
		'preclose':'last_close', 	# 昨收价（美元）

		'open':'open', 			# 开盘价（美元）
		'high':'high', 			# 最高价（美元）
		'low':'low', 			# 最低价（美元）

		'amplitude':'amplitude', 	# 振幅 （用小数表示真实振幅，例：0.02 就表示振幅为2%）
		'volume':'volume', 		# 成交量（股）

		'mktcap':'total_value', # 总市值（美元）
		'pe':'pe', 				# 市盈率
		'market':'market', 		# 所属市场
		'category_id':'industry_id'	# 行业 id		
		}
	
	all_df = None 			# 存放美股所有股行情
	[total_page, df] = get_total_page_from_sina()
	if total_page <= 1:
		return df

	all_df = df
	base_url = cf.URL_DICT['SINA3']
	url_arr = []
	for page_num in range(2, total_page+1):
		url = base_url % (page_num)
		url_arr.append(url)
	
	#page_source_arr = get_page_by_gevent(url_arr=url_arr)
	page_source_arr = get_page(url_arr=url_arr)
	if page_source_arr is None:
		return None
		
	reg = '{.*\)' 			# 提取数据用的正则
	# 下面这个 for , 从上面最早返回的协程中提取 value，并 kill 掉其他还没完成的协程。
	for k,page_source in enumerate(page_source_arr):
		#print('%d / %d' % (k,total_page))
		if page_source is None:
			continue
		# ----------------
		arr = re.findall(reg, page_source)
		if len(arr) == 0:
			continue
		
		# 根据分析，返回的 arr 只有一个元素，即 arr[0]，这个元素是一个 json，包含了所有数据，
		# 下面去掉这串 json 字符串中最后一个多余的字符')'，剩下的就是可转成 dict 的标准 json 结构，于是把他转成 dict
		data_json = arr[0][:-1]
		data_dict = json.loads(data_json) 			# 把 json 转成 dict
		# 下面从 data_dict 中提取一个 key 为 'data' 的元素，这个元素本身是 list，即下面这个 sub_data_arr
		# 这个 sub_data_arr 中的各个元素还是 dict，所以要把这个 sub_data_arr 转成 json ，
		# 以便 pandas 的 read_json() 能够读取并直接转成 df 格式
		sub_data_arr = data_dict['data']
		sub_data_json = json.dumps(sub_data_arr) 	# 转成 json，以便下面的 pd.read_json() 能够读取		
		df = pd.read_json(sub_data_json, orient='records', dtype=False) 		# dtype = False 表示读取时不要自动推断类型，这样可保留原汁原味
		all_df = pd.concat([all_df,df])
		
	all_df = all_df.rename(columns=column_dict) 			# 对列改名

	# 将振幅中的 % 去掉，以便后续可以数值转换
	all_df['amplitude'] = all_df['amplitude'].replace('[%]','',regex=True) 						# 把这 3 列中的 % 去掉，并且除以100
	# --------------------------------------------
	# 这些数值列转成 float
	float_column_arr = ['last_close','open','high','low','price','price_change','percent','amplitude','total_value','pe']
	all_df = jxb.convert_df_type(df=all_df, xtype=float, column_arr=float_column_arr)
	# 这些数值列转成 int
	int_column_arr =  ['volume','industry_id']
	all_df = jxb.convert_df_type(df=all_df, xtype=int, column_arr=int_column_arr)
	# 把以下单位转成标准单位
	for col in ['percent','amplitude']:
		all_df[col] /= 100
	# 调整  df 中的列顺序，使之按 STOCK_COLUMN_ORDER_ARR 中的顺序排列
	all_df = jxb.sort_df_column(df=all_df, column_arr=cf.STOCK_COLUMN_ORDER_ARR)
	# ==========================
	# df = df.sort_values(by=['code'],ascending=[True]) 		# 这里不要按股票代码排序，用户传进来是什么顺序就保持他的顺序。
	all_df = all_df.reset_index(drop=True)	
	
	return all_df









def get_total_page_from_sina():
	"""
	说明：从新浪美股行情这一节爬取第 1 页美股行情（每页约60行）及总页数
	参数：无
	返回值：是一个 list，包含两个元素，第一个元素是总页数(int类型)，第2个元素是一个 df，存放的是新浪美股行情的第一页
	"""
	result_arr = []			# 存放总页码及首页美股行情df
	
	total_page = 1 			# 预设新浪美股行情表格总页数为 1
	base_url = cf.URL_DICT['SINA3']
	url_arr = [base_url % (1)]
	
	page_source_arr = get_page(url_arr=url_arr)
	if page_source_arr is None:
		return None

	total_row = 0 			# 预设总行数为0
	page_source = page_source_arr[0]
	if page_source is None:
		return None
	# ----------------
	reg = '{.*\)' 			# 提取数据用的正则
	arr = re.findall(reg, page_source)
	if len(arr) == 0:
		return None
	
	data_json = arr[0][:-1]
	data_dict = json.loads(data_json)
	total_row = int(data_dict['count'])

	sub_data_arr = data_dict['data']
	sub_data_json = json.dumps(sub_data_arr)
	df = pd.read_json(sub_data_json, orient='records')

	if len(df) > 0:
		total_page = int(total_row/len(df)) + 1
		
	result_arr = [total_page, df]
	
	return result_arr










	

# sina data end
# ==================================

# ---------------------------------
# netease data start

def get_netease_realtime_stock_url(code_arr, index=False):
	"""
	说明：该函数根据传入的股票代码数组，生成网易 netease 实时股票行情的网址返回
	参数：code_arr: 股票代码列表；index： 表示code_arr 里的股票代码是否表示指数
	返回值：指向网易 netease 实时行情的网址。
	"""
	if code_arr is None or len(code_arr)==0:
		print(jxb.get_current_function_name() + ': 错误！传入的股票代码列表 code_arr 不能为空。')
		return None

	base_url='http://api.money.126.net/data/feed/%smoney.api' 			# 选择 netease 实时数据源	

	prefixed_code_arr = get_prefixed_code_arr(code_arr=code_arr, by='number', index=index) 	# 对股票代码数组中的每一只股加上市场代码前缀后返回，仍然是数组形式
	prefixed_code_str = ','.join(prefixed_code_arr)
	prefixed_code_str += ',' 
	url = base_url % (prefixed_code_str) 		# 将实际值（即 % 后面括号里的值）代入到 base_url 中去

	return url








def get_netease_realtime_stock_data_from_page_source(page_source):
	"""
	说明：根据传入的股票代码数组，根据经验最好一次性不超过 1000 只，到网易netease 获取实时数据，以 df 形式返回
	参数：code_arr, 待取实时数据的股票代码列表，index 表示是否是指数，默认 False
	返回值：df, 相应股票的实时数据，df 格式
	"""
	if page_source is None:
		return None

	func_name = jxb.get_current_function_name()
	# 构造网易股票实时行情列头名称映射，由于是 DICT 方式映射，所以 DICT 内可以不考虑顺序。
	column_dict = {
		'ask1':'ask1_price', 	# 卖一价（元）
		'ask2':'ask2_price', 	# 卖二价（元）
		'ask3':'ask3_price', 	# 卖三价（元）
		'ask4':'ask4_price', 	# 卖四价（元）
		'ask5':'ask5_price', 	# 卖五价（元）
		'askvol1':'ask1_volume', 	# 卖一量（股）
		'askvol2':'ask2_volume', 	# 卖二量（股）
		'askvol3':'ask3_volume', 	# 卖三量（股）
		'askvol4':'ask4_volume', 	# 卖四量（股）
		'askvol5':'ask5_volume', 	# 卖五量（股）

		'bid1':'bid1_price', 	# 买一价（元）
		'bid2':'bid2_price', 	# 买二价（元）
		'bid3':'bid3_price', 	# 买三价（元）
		'bid4':'bid4_price', 	# 买四价（元）
		'bid5':'bid5_price', 	# 买五价（元）
		'bidvol1':'bid1_volume', 	# 买一量（股）
		'bidvol2':'bid2_volume', 	# 买二量（股）
		'bidvol3':'bid3_volume', 	# 买三量（股）
		'bidvol4':'bid4_volume', 	# 买四量（股）
		'bidvol5':'bid5_volume', 	# 买五量（股）

		'high':'high', 		# 最高价（元）
		'low':'low', 		# 最低价（元）
		'name':'name', 		# 名称
		'open':'open', 		# 开盘价（元）
		'percent':'percent', 		# 涨幅（用小数表示真实涨幅，例：0.02 就表示涨2%）
		'price':'price', 		# 市价（元）
		'symbol':'code', 		# 代码

		'turnover':'amount', 		# 成交额（元）
		'updown':'price_change', 		# 涨跌（元）
		'volume':'volume', 		# 成交量（股）

		'yestclose':'last_close', 	# 昨收价（元）

		'date':'date', 		# 日期
		'time':'time'			# 时间		
		}

	df = None
	try:
		# 从网易返回的实时数据看，取这个范围可以得到 json 格式的股票实时数据
		data_json = page_source[21:-2] 
		# 下面的orient 取 'index' 也是从上面返回的 json 数据分析而来的，dtype={'symbol':str} 表示在读取数据时保持 'symbol' 这个字段的类型为 str，
		# dtype=True 表示由pandas 自己推断数据，这往往不符合要求；dtype=False 表示不要 pandas 推断，原来是怎样就怎样。
		# read_json() 的具体参数请查阅pandas		
		df = pd.read_json(data_json, orient='index', dtype=False) 		
		# 把 time 列按空格拆分成两列形成 df 返回(expand=True 表示形成 df，否则是 list)
		date_time_df = df.time.str.split(' ', expand=True) 	# 将 time列（观察网易返回的数据中的 time 列包含了日期和时间，两者以空格分隔）分成两列，expand=True 表示以 DF 形式返回
		date_time_df.columns=['date','time'] 				# 配上（或叫更改）列名
	except:
		print(func_name,' 错误！企图从页面提取 json数据出错，可能页面并非是 json 格式。')
		return None
	
	# 删除以下这些列
	for col in ['arrow','code','status','type','update','time']:
		df.pop(col)

	#df[date_time_df.columns] = date_time_df 		# 这句也是正确的，但用下面这句更清晰一些
	df = pd.concat([df,date_time_df], axis=1) 		# axis=1 表示拼列（若不指定 axis则其默认值为 0，表示拼行）
	df['date'] = df['date'].str.replace('/','-') 	# 网易实时数据返回的 date 列是 / 分割的，这里将其转成 - 分割
	# 替换 df 的列名到 column_arr 中指定的列名，注意：column_arr 中的顺序不能随意调整，它是事先了解了 df 中的顺序后编排的。
	# df.columns = column_arr 
	df = df.rename(columns=column_dict)	 			# 更改列名到标准名称
	# 下面的 code 列就是股票代码。由于 pandas.read_json() 后将股票代码当作了数值并去掉了前导0，
	# 所以这里要将其转成字符串，并调用字符串的方法右对齐左侧补数个 char 直到有 width 个: rjust(width,char)
	# 后面发现 pd.read_json() 中指定 dtype 参数为 dict 时，可以在读取 json 时明确指定哪些字段为哪些类型，所以下面这两行转换用不到了
	# 	df['code'] = df['code'].astype(dtype=str)
	# 	df['code'] = df['code'].str.rjust(6,'0') 		

	# --------------------------------------------
	# 这些数值列转成 float
	float_column_arr = ['last_close','open','high','low','price','amount','bid1_price','bid2_price','bid3_price','bid4_price','bid5_price','ask1_price','ask2_price','ask3_price','ask4_price','ask5_price','price_change','percent']
	df = jxb.convert_df_type(df=df, xtype=float, column_arr=float_column_arr)
	# 这些数值列转成 int
	int_column_arr =  ['volume','bid1_volume','bid2_volume','bid3_volume','bid4_volume','bid5_volume','ask1_volume','ask2_volume','ask3_volume','ask4_volume','ask5_volume']
	df = jxb.convert_df_type(df=df, xtype=int, column_arr=int_column_arr)
	# 调整  df 中的列顺序，使之按 STOCK_COLUMN_ORDER_ARR 中的顺序排列
	df = jxb.sort_df_column(df=df, column_arr=cf.STOCK_COLUMN_ORDER_ARR)
	# ==========================
	# df = df.sort_values(by=['code'], ascending=[True]) 				# 这里不要按股票代码排序，用户传进来是什么顺序就保持这个顺序。
	df = df.reset_index(drop=True)

	return df










def get_k_stock_data(code, xbegin=None, xend=None, index=False, k_level='d', source='netease'):
	"""
	说明：本函数调用相应源的接口获取相应级别的K线数据
	"""
	df = None
	if source is None:
		source = 'netease'
	if source.upper() == 'NETEASE':
		df = get_netease_k_stock_data(code=code, xbegin=xbegin, xend=xend, index=index, k_level=k_level)
	
	return df







def get_netease_k_stock_data(code, xbegin=None, xend=None, index=False, k_level='d'):
	"""
	说明：该函数从网易获取K线数据
	参数：code: 股票代码；xbegin: 起始日期；xend: 结束日期； index: 是否指数
	返回值：K线数据（df 格式）
	"""
	func_name = jxb.get_current_function_name() + ': '
	if xbegin is None or xend is None or str(xbegin) > str(xend):
		print(func_name + '错误！请输入起始日期和结束日期，并确保起始日期小于或等于结束日期')
		return None
	
	if k_level.upper() != 'D':
		print(func_name + ' sorry, 本接口暂时只能获取股市日 K 线数据，无法获取其他级别的 K 线数据。')
		print('通过给参数 k_level 传入 "D" 可获取股市日 K 线数据')
		return None
		
	# print(func_name, "注意：网易返回的 K线数据可能不是十分准确，请小心使用！")

	# 要从网易拉取历史K线数据的各列名称（不要改变顺序）：
	k_col_arr = [
		'date', 			# 日期
		'code', 			# 股票代码
		'name', 			# 股票名称
		'open', 			# 开盘价（元）
		'high', 			# 最高价（元）
		'low', 				# 最低价（元）
		'close', 			# 收盘价（元）
		'last_close', 		# 昨收价（元）
		'price_change', 			# 涨跌额（元）
		'percent', 			# 涨幅（用小数表示真实涨幅）
		'volume', 			# 成交量（股）
		'amount', 			# 成交额（元）
		'turnover', 		# 换手率（用小数表示真实换手率）
		'total_value', 		# 总市值（元）
		'circulation_value' # 流通值（元）
		]

	k_df = None 			# 该变量用于存放K线数据（dataframe 格式），赋初值 None
	url = get_netease_k_data_url(code=code, xbegin=xbegin, xend=xend, index=index) 		# 根据指定的股票代码和日期范围，生成网易K线数据源 url 
	retry_count = 10 			# 计数器，表示尝试几次
	xcount = 0
	page_source = None
	# 用循环和异常拉数据，因为拉数据时太频繁经常要被服务器踢
	while True:
		if xcount > retry_count:
			return None
		try:
			# 下面两句是一样的，随便用哪句都可以，他们只是用不同的模块来实现相同的功能
			#page_source = get_page_by_urllib(url=url) 				# 到指定的数据源网址下载数据（这里下载下来是包含数据的页面源码，已解码，已经是纯文本格式）
			#page_source=page_source.decode('gbk')
			#page_source = get_page_by_requests(url=url) 				# 到指定的数据源网址下载数据（这里下载下来是包含数据的页面源码，已解码，已经是纯文本格式）
			page_source_arr = get_page([url])
			if page_source_arr is not None:
				page_source = page_source_arr[0]
		except:
			s = random.randint(1,5)
			print(func_name,'\n可能节假日休息，没能从网易取到 K 线数据，休息 %s 秒后将自动继续尝试拉数据。' % (str(s)))
			time.sleep(s) 			# 如果被服务器踢，则停止3秒再拉数据
			xcount += 1
			continue
		else:
			if page_source is None:
				xcount += 1
				continue
			else:
				if page_source.find('html') >= 0:
					print('返回了 html 数据，没有返回 K 线数据，网易服务器可能出问题了，不再尝试。')
					return None
				else:
					break

	page_arr = page_source.split('\r\n') 		# 返回的 page是一条长长的字符，以分割符 \r\n 将这长长的字符串切断，并把每段字符串保存到数组 page_arr 中
	#col_arr = page_arr[0].split(',') 			# page_arr 中第一个元素（即字符串）为中文列名串接，提取这些列名到数组 col_arr 中
	if len(page_arr) >= 2:
		k_data_arr = page_arr[1:] 			# 从 page_arr 中的第2个元素开始为真正的 k 线数据，但这里他们仍是字符串形式的，需要转化成数组

		k_data_arr = [x.replace("'",'') for x in k_data_arr] 		# 把上述 k_data_arr 中的所有 K线数据中的 ' 号替换为空，即去掉 ' 号
		k_data_arr = [x.split(',') for x in k_data_arr] 			# 将 k_data_arr 中每一行字符串形式的K线数据，转换成 list 形式，这样转换后， k_data_arr 中的每一个元素都成了数组
		k_data_arr = k_data_arr[:len(k_data_arr)-1] 				# 因为网易返回的数据最后一行全是 None ，所以要去掉
		k_df = pd.DataFrame(data=k_data_arr, columns=k_col_arr)  	# 把数组形式的K线数据，转换成 DataFrame 形式，以便进一步操作
		k_df.code = code 			# 加这一句的目的是因为传入的指数代码与网易数据源所需的指数代码形式不同所致，从网易拿回数据后，将指数代码恢复成我们自己传入的指数代码形式

		if len(k_df)>0:
			k_df = k_df.sort_values(by=['date'], ascending=True)
			k_df = k_df.reset_index(drop=True) 					# 用自然数行索引去替换原行索引
			#k_df = wash_data(df=k_df, ds=ds, index=index) 		# 再调用自定义函数清洗
			k_df = wash_netease_k_data(df=k_df, index=index) 	# 调用网易K线处理函数
			# --------------------------------------------
			# 这些数值列转成 float
			float_column_arr = ['open','high','low','close','last_close','price_change','percent','amount','turnover','total_value','circulation_value']
			k_df = jxb.convert_df_type(df=k_df, xtype=float, column_arr=float_column_arr)
			# 这些数值列转成 int
			int_column_arr =  ['volume']
			k_df = jxb.convert_df_type(df=k_df, xtype=int, column_arr=int_column_arr)
			for col in ['percent','turnover']:
				k_df[col] /= 100 				# 将涨幅和换手率转成小数
			# 调整  df 中的列顺序，使之按 STOCK_COLUMN_ORDER_ARR 中的顺序排列
			k_df = jxb.sort_df_column(df=k_df, column_arr=cf.STOCK_COLUMN_ORDER_ARR)
			# ==========================
			k_df = k_df.sort_values(by=['date'], ascending=[True]) 
			k_df = k_df.reset_index(drop=True)
		
	return k_df









def get_netease_k_data_url(code, xbegin=None, xend=None, index=False):
	"""
	说明：构造网易历史 K线数据源 url
	参数：code: 6位股票代码；xbegin: 开始日期（可以是字符串形式或 python日期格式）；xend: 结束日期； index: 是否指数；
	返回值：url
	"""

	func_name = jxb.get_current_function_name() + ': '	 			# 获取函数名
	xtoday = jxb.get_today()
	if xbegin is None:
		xbegin = datetime.date(xtoday.year,1,1) 					# 构造本年第1天
	if xend is None:
		xend = xtoday

	url = ''
	base_url = 'http://quotes.money.163.com/service/chddata.html?code=%s&start=%s&end=%s&fields=TOPEN;HIGH;LOW;TCLOSE;LCLOSE;CHG;PCHG;VOTURNOVER;VATURNOVER;TURNOVER;TCAP;MCAP' 		# 网易历史数据源

	if (not jxb.is_valid_date(str(xbegin))) or (not jxb.is_valid_date(str(xend))):
		print(func_name + '输入的日期或格式有误')
		return None

	d1 = ''.join(str(xbegin).split('-')) 		# 调整日期格式，以适应163接口
	d2 = ''.join(str(xend).split('-'))
	#prefixed_code_arr = get_prefixed_code_arr(code_arr=[code], by='number', index=index) 	# 对股票代码数组中的每一只股加上市场代码前缀后返回，仍然是数组形式
	#prefixed_code = prefixed_code_arr[0]
	prefixed_code = cnstock.get_prefixed_code(code=code, by='number', index=index)

	if prefixed_code is not None:
		url = base_url % (prefixed_code,d1,d2) 		# 将实际值（即 % 后面括号里的值）代入到 base_url 中去

	return url









def wash_netease_k_data(df, index=False):
	"""
	说明：对网易K线数据进行处理
	参数：df: 网易K线数据；index: 是否指数
	返回值：处理后的K线数据（df格式）
	"""
	if len(df) == 0:
		return df

	index1_arr = list(df.index)
	code = df.loc[index1_arr[0],'code']

	# 先遍历所有行，去掉 涨跌额为 'None' 的行
	for i in index1_arr:
		if index :
			# 指数进入这里
			if df.loc[i,'price_change'] == 'None':
				if df.loc[i,'last_close'] == 'None':
					df.loc[i,'last_close'] = df.loc[i,'open'] 			# 如果昨收价不存在，一般是首个交易日，则令其昨收价等于今天开盘价，方便程序处理
				df.loc[i,'price_change']=str(float(df.loc[i,'close']) - float(df.loc[i,'last_close']))
				df.loc[i,'percent']=str((float(df.loc[i,'close']) - float(df.loc[i,'last_close'])) / float(df.loc[i,'last_close']))	
			# 发现中小板指在早期时，即2008-06-27 日及以前的成交额都是 'None', 故用 0 去替换
			if df.loc[i,'amount'] == 'None':
				df.loc[i,'amount'] = 0
		else:
			# 普通股进入这里，因为网易返回的普通股当 price_change 为'None' 时，则当天的 open,high,low.close等全为0 了，所以这行数据就不要了，直接 drop 掉
			if df.loc[i,'price_change'] == 'None':
				df = df.drop(i,axis=0)

	df = df.replace(['None'],[0]) 			# 把 raw 数据中剩余的所有'None' 都替换为 0

	if len(df) == 0:
		return df

	# 下面这个 if 是判断指数的，由于指数没有换手率，总市值，流通值等概率，所以给他们置0
	if index :
		df['turnover'] = 0
		df['total_value'] = 0
		df['circulation_value'] = 0

	index1_arr=list(df.index)

	# -------------------------------------
	# 这一节是特殊情况特殊处理
	# 1. 对于000046 这只股，在 1994/9/19，1994/9/16，1994/9/15，1994/9/14，1994/9/13，1994/9/12 这6 个交易日里，其换手率数据为 None，流通值也为 0，所以需要补全
	# 好在该股在这些天有总市值数据，并且根据上述日期附近的总市值和流通值之比（大概4倍），可以近似推算出上述6个交易日的，流通值，再利用成交额数据可近似算出换手率
	if code == '000046':
		temp_index_arr = [] 		# 临时数组，用于存放换手率为 None 的那些行标
		for i in index1_arr:
			if df.loc[i,'turnover'] == 'None':
				df.loc[i,'turnover'] = 0
				temp_index_arr.append(i)
		# 把这三列的数据类型先转换成 float （原先是 string 类型，这是网易返回的默认类型），以便下面进行数学计算
		df.amount = df.amount.astype(dtype=float)
		df.turnover = df.turnover.astype(dtype=float)
		df.total_value = df.total_value.astype(dtype=float)
		df.circulation_value = df.circulation_value.astype(dtype=float)
		# 下面计算缺失的换手率和流通值
		for i in temp_index_arr:
			df.loc[i,'circulation_value'] = df.loc[i,'total_value'] * 0.25 			# 先计算出流通值
			df.loc[i,'turnover'] = df.loc[i,'amount'] * 100 / df.loc[i,'circulation_value'] 		# 再计算出换手率。注意，换手率是用成交额除以流通值（元）得来的，不是除以总市值！

	if code == '600653':
		temp_index_arr = [] 		# 临时数组，用于存放换手率为 None 的那些行标
		for i in index1_arr:
			if df.loc[i,'turnover'] == 'None':
				df.loc[i,'turnover'] = 0
				temp_index_arr.append(i)
		# 把这三列的数据类型先转换成 float （原先是 string 类型，这是网易返回的默认类型），以便下面进行数学计算
		df.amount = df.amount.astype(dtype=float)
		df.turnover = df.turnover.astype(dtype=float)
		df.total_value = df.total_value.astype(dtype=float)
		df.circulation_value = df.circulation_value.astype(dtype=float)
		# 下面计算缺失的换手率和流通值
		for i in temp_index_arr:
			df.loc[i,'circulation_value'] = df.loc[i,'total_value'] * 0.682 			# 先计算出流通值
			df.loc[i,'turnover'] = df.loc[i,'amount'] * 100 / df.loc[i,'circulation_value'] 		# 再计算出换手率。注意，换手率是用成交额除以流通值（元）得来的，不是除以总市值！

	# 特殊处理到这里结束
	# =====================================

	return df

# netease data end
# ==================================





# ---------------------------------
# tencent data start
	
def get_tecent_realtime_stock_url_backup(code_arr, index = False):
	'''
	说明：该函数根据传入的股票代码数组
	返回一个适合数据源（实际上是 tencent 的realtime 数据源）的URL
	'''	

	func_name = jxb.get_current_function_name() + ': '

	if len(code_arr)==0:
		print(func_name + '错误！传入的数组 code_arr 不能为空。')
		return None

	base_url = "http://qt.gtimg.cn/q=%s" 			# tencent 实时数据源
	convert_code_arr = []
	sh_code_arr = ['5','6','9']

	# 指数代码直接进入 if ，因为相信传入时其是带前导符'sh' 或 'sz' 的，无需再添加；而普通股票代码认为传入时是不带前导符的，所以进入 else 用 for 循环判断后添加
	if index == True:
		convert_code_arr = code_arr 				
	else:
		for i,code in enumerate(code_arr):
			temp_code = None
			'''
			if code[:2] in '60':
				temp_code = 'sh' + code
			if code[:2] == '30' or code[:2] == '00':
				temp_code = 'sz' + code
			'''
			if code[:1] in sh_code_arr:
				temp_code = 'sh' + code
			else:
				temp_code = 'sz' + code

			if temp_code is not None:
				convert_code_arr.append(temp_code)
	
	code_str = ','.join(convert_code_arr)
	
	url = base_url % (code_str) 		# 将实际值（即 % 后面括号里的值）代入到 base_url 中去

	return url








def get_tencent_realtime_stock_url(code_arr, index=False):
	"""
	说明：该函数根据传入的股票代码数组，生成腾讯实时股票行情的网址返回
	参数：code_arr: 股票代码列表；index： 表示code_arr 里的股票代码是否表示指数
	返回值：指向腾讯实时行情的网址。
	"""
	if code_arr is None or len(code_arr)==0:
		print(jxb.get_current_function_name() + ': 错误！传入的股票代码列表 code_arr 不能为空。')
		return None

	#base_url = 'http://hq.sinajs.cn/list=%s' 			# 选择 sina 实时数据源
	base_url = "http://qt.gtimg.cn/q=%s" 			# tencent 实时数据源

	prefixed_code_arr = get_prefixed_code_arr(code_arr=code_arr, index=index) 	# 对股票代码数组中的每一只股加上市场代码前缀后返回，仍然是数组形式
	prefixed_code_str = ','.join(prefixed_code_arr)
	prefixed_code_str += ','
	url = base_url % (prefixed_code_str) 		# 将实际值（即 % 后面括号里的值）代入到 base_url 中去

	return url








def get_tencent_realtime_stock_data_from_page_source(page_source):
	"""
	说明：根据传入的股票代码数组，到腾讯获取实时数据，以 df 形式返回，根据经验最好一次性不超过 900 只
	参数：code_arr, 待取实时数据的股票代码列表，index 表明是否指数
	返回值：df, 相应股票的实时数据，df 格式
	"""
	if page_source is None:
		return None

	func_name = jxb.get_current_function_name()
	# 构造腾讯股票实时行情列头名称，由于腾讯返回的数据是没有 key 的，即是纯数据，而不是 dict 方式，所以他返回的数据是有顺序，
	# 所以这里给他配的列头不要更改顺序！				  
	column_arr = [
		'name', 		# 名称
		'code', 		# 代码
		'price', 		# 市价（元）
		'last_close', 	# 昨收价（元）
		'open', 		# 开盘价（元）
		
		'temp_volume', 	# temp
		
		'outer_volume', 	# 外盘（股）
		'inner_volume',		# 内盘（股）
		
		'bid1_price', 	# 买一价（元）
		'bid1_volume', 	# 买一量（股）
		'bid2_price', 	# 买二价（元）
		'bid2_volume', 	# 买二量（股）
		'bid3_price', 	# 买三价（元）
		'bid3_volume', 	# 买三量（股）
		'bid4_price', 	# 买四价（元）
		'bid4_volume', 	# 买四量（股）
		'bid5_price', 	# 买五价（元）
		'bid5_volume', 	# 买五量（股）

		'ask1_price', 	# 卖一价（元）
		'ask1_volume', 	# 卖一量（股）
		'ask2_price', 	# 卖二价（元）
		'ask2_volume', 	# 卖二量（股）
		'ask3_price', 	# 卖三价（元）
		'ask3_volume', 	# 卖三量（股）
		'ask4_price', 	# 卖四价（元）
		'ask4_volume', 	# 卖四量（股）
		'ask5_price', 	# 卖五价（元）
		'ask5_volume', 	# 卖五量（股）
		
		'temp_latest_tick', 	# temp
		
		'time', 		# 时间
		'price_change',		# 涨跌额（元）
		'percent', 		# 涨幅（用小数表示真实涨幅，例：0.02 就表示涨幅为2%）	
		'high', 		# 最高价（元）
		'low', 			# 最低价（元）

		'temp_price_volume_amount', 		# temp
		
		'volume', 		# 成交量（股）
		'amount', 		# 成交额（元）
		'turnover', 	# 换手率（用小数表示真实换手率，例：0.02 就表示换手率为2%）
		
		'pe_ttm', 		# 滚动市盈率

		'temp_unknown1', 	# temp
		'temp_high', 		# temp
		'temp_low', 		# temp

		'amplitude', 	# 振幅（用小数表示真实振幅，例：0.02 就表示振幅为2%）
		'circulation_value', 		# 流通值（元）
		'total_value', 				# 总市值（元）
		'pb', 			# 市净率
		
		'max_price', 	# 最高价（元）
		'min_price', 	# 最低价（元）
		
		'liangbi', 		# 量比
		'weicha', 		# 委差
		
		'average_price', 	# 均价
		'pe_dynamic', 	# 动态市盈率
		
		'pe_static', 	# 静态市盈率
		'temp1',		# temp
		'temp2', 		# temp
		'temp3', 		# temp
		'temp4', 		# temp
		'amount_after', # 盘后额（元）
		'volume_after',	# 盘后量（手）
		'temp7' 		# temp
		
		]

	# 设几个初始变量
	data_arr = [] 		# 存放新浪返回的行情数据 
	#df = None 			# 存放将上述行情数据转成 dataframe 格式后的数据
	
	# 流程进到这里表示拿到了行情数据，下面对数据进行提取和规范，形成 df 返回
	arr = page_source.split(';')
	arr = arr[:-1] 			# 表示去掉最后一个元素
	for i in arr:
		arr2 = i.split('=')
		arr2 = arr2[1].split('~')
		arr2 = arr2[1:-1] 			# 去掉第一个和最后一个元素
		arr2 = arr2[:len(column_arr)] 		# 从 arr2 中截取前 N 个，使得长度与列名长度保持一致，否则装配不上。
		data_arr.append(arr2)

	df = pd.DataFrame(data=data_arr, columns=column_arr) 			# 构造 DF， 并配上列头
	if len(df) == 0:
		print(func_name,' 错误！没有数据。')
		return None
	# ---------------------
	# 以上得到的这个 df 是来自腾讯的原始数据，未做扔何改动，
	# 下面对这个 df 进行一些变换，如：去掉无用列，统一量纲等等
	# 先去掉 'temp' 开头的列
	for i,col in enumerate(column_arr):
		if col.startswith('temp') == True:
			df.pop(col)

	# 把name, code, time 以外的列先全部转成 float
	float_column_arr = list(set(df.columns.tolist()) - set(['name','code','time']))
	df = jxb.convert_df_type(df=df, xtype=float, column_arr=float_column_arr) 			# 对这些列进行类型转换，转换不了的数据项在 convert_df_type() 中用 0 填充了

	# 股票代码要转成字符串，并补足前导0，所以这里要将其转成字符串，并调用字符串的方法右对齐左侧补数个 char 直到有 width 个: rjust(width,char)
	df['code'] = df['code'].astype(dtype=str).str.rjust(6,'0') 	
	# 从原始 time 列中提取日期和时间				
	df['date'] = df['time'].str.slice(0,4) + '-' + df['time'].str.slice(4,6) + '-' + df['time'].str.slice(6,8)
	df['time'] = df['time'].str.slice(8,10) + ':' + df['time'].str.slice(10,12) + ':' + df['time'].str.slice(12,14)

	'''
	# ---------------------------
	# 1. before 9:25, 先传递一些列，补上已有的列的空白处
	if  jxb.hms_to_timestamp(xtime=stock_default_rule_dict['OPEN_TIME']) <= time.time() <= jxb.hms_to_timestamp(xtime=stock_default_rule_dict['OPEN_PRICE_TIME']):
		# 在9：25前，如果成交量从有变为 0 ，说明庄撤单了，但这时市价 price 还留在撤单前撮合时的价格，这是错误的，应当改为昨收价，其他各个价也必须回到昨收价，并且腾讯原生幅度 percent 也要改为 0，因为腾讯是根据 price 计算的，我们把 price 改回昨收价之后，同时也要把 percent 改回0
		df['percent'][df['bid1_volume'] == 0] = (df['percent'] - df['percent'])[df['bid1_volume'] == 0]
		df['price'][df['bid1_volume'] == 0] = df['last_close'][df['bid1_volume'] == 0] 			# 等式两头后面的中括号表示df筛选条件，条件之前的内容表示赋值。这句话的意思就是在 9：25前若撮合的成交量为 0 的话，则让市价回到昨收价

		# 在9：25前，以下5个价要和 price 保持一致。
		df['bid1_price'] = df['price']
		df['ask1_price'] = df['price']
		# -----------------------
		df['open'] = df['price'] 			# 因为 9:25 前 open , high, low 为 0，所以用 price 当作动态开盘价. 注意：新浪数据在9：25前price 值是没有的，必须用 bid1 来代替，而腾讯数据在9：25前是有 price 值的，也有 price_change 和 percent 值
		df['high'] = df['price']
		df['low'] = df['price']

		df['volume'] = df['bid1_volume']
	# ==========================
	'''
	
	# ------------------------------
	# 2. 下面转换数据类型及统一单位到基本单位（即以元计价，而不是以万元或亿元；以股计成交量等，而不是以手或万手等；以真实的比例计换手率、百分比等，而不是放大100倍成一个整数来计）
	# 这个 for 把所有的量（成交量，买1到买5的量，卖1到卖5的理，内盘外盘的量等）从手转化成股
	int_column_arr =  ['volume','outer_volume','inner_volume','bid1_volume','bid2_volume','bid3_volume','bid4_volume','bid5_volume','ask1_volume','ask2_volume','ask3_volume','ask4_volume','ask5_volume','weicha','volume_after']
	for i,col_name in enumerate(int_column_arr):
		df[col_name] = df[col_name].astype(dtype=int) * stock_default_rule_dict['ONE_HAND']

	# 这个 for 把各种值（流通值，总市值等）从亿元转化成元
	for i,col_name in enumerate(['circulation_value','total_value']):
		df[col_name] *= 100000000 					# 将流通值，总市值单位从亿元改成元

	# 这个 for 把各种幅度（涨幅，换手率，振幅等），从光用分子表示转化成除以100后的小数表示，以表示真实的幅度
	for i,col_name in enumerate(['percent','turnover','amplitude']):
		df[col_name] /= 100

	# 这个 for 把各种万元（如成交额 amount）改成元
	for i,col_name in enumerate(['amount','amount_after']):
		#df[col_name] = df[col_name].astype(dtype=int) * 10000 			# 将成交额单位从万元改成元
		df[col_name] *=  10000 			# 将成交额单位从万元改成元
	# ===================================

	# -----------------------------
	# 3. 以下这些列是腾讯数据没有提供的，是根据腾讯提供的数据计算出来后额外添加到 df 上的

	# ===========================

	# -------------------------
	# 4. 下面这个 if 用来判断 9：25 前要设置的一些列值，因为这些列值在 9：25前集合竞价阶段腾讯行情数据里没有提供, 这些列值依赖上面第3条的计算结果，所以没法挪到第1条与其合并
	if  jxb.hms_to_timestamp(xtime=stock_default_rule_dict['OPEN_TIME']) <= time.time() <= jxb.hms_to_timestamp(xtime=stock_default_rule_dict['OPEN_PRICE_TIME']):
		df['amount'] = df['bid1_price'] * df['bid1_volume']
		df['turnover'] = df['amount'] / df['circulation_value'] 			# 注意：换手率是用成交额除以流通值（元）得来的，不是除以总市值。

		# 如果9：25前没有 percent 这个值，就打开下面这个注释
		# df['percent'] = (df['price'] - df['last_close']) / df['last_close']

	# ==================================
	# --------------------------------------------
	# 调整  df 中的列顺序，使之按 STOCK_COLUMN_ORDER_ARR 中的顺序排列
	df = jxb.sort_df_column(df=df, column_arr=cf.STOCK_COLUMN_ORDER_ARR)
	# ==========================
	# df = df.sort_values(by=['code'],ascending=[True]) 		# 这里不要按股票代码排序，用户传进来是什么顺序就保持他的顺序。
	df = df.reset_index(drop=True)

	return df












def get_stock_fund_flow(code, index=False, source='tencent'):
	"""
	说明：从指定源获取指定股票的主力和散户资金流向
	参数：code: 需要获取资金流行的股票代码; index: 是否指数，一般设为 False；source: 从哪个源获取
	返回值：资金流向数据（df 格式）
	"""
	df = None
	if source.upper() in ['TENCENT','QQ']:
		df = get_tencent_stock_fund_flow(code=code, index=index)

	return df








def get_tencent_stock_fund_flow(code, index=False):
	"""
	说明：从腾讯源获取指定股票的主力和散户资金流向
	参数：code: 需要获取资金流行的股票代码
	返回值：资金流向数据（df 格式）
	"""
	column_arr = [
		'code', 			# 股票代码
		'main_in', 			# 主力资金流入（元）
		'main_out',			# 主力资金流出（元）
		'main_net_in',		# 流力资金净流入（元）
		'temp1',			# 主力资金流入流出总和
		'personal_in',		# 散户资金流入（元）
		'personal_out', 	# 散户资金流出（元）
		'personal_net_in', 	# 散户资金净流入（元）
		'temp2', 			# 散户资金流入流出总和
		'total_fund_in',		# 资金流入总和（元）
		'temp3',			# 未知1
		'temp4', 			# 未知2
		'name',				# 股票名称
		'date',				# 日期
		]
	
	# 腾讯资金流向数据接口
	base_url = "http://qt.gtimg.cn/q=ff_%s"
	prefixed_code = cnstock.get_prefixed_code(code=code, index=index)
	url = base_url % (prefixed_code)

	# page_source = get_page_by_requests(url=url)
	
	page_source = None
	page_source_arr = get_page([url])
	if page_source_arr is not None:
		page_source = page_source_arr[0]
		
	if page_source is None:
		return None
	
	arr = page_source.split('"')
	arr = arr[1].split('~')
	arr = arr[:14]
	# 构造 df
	df = pd.DataFrame(data=[arr],columns=column_arr)
	# 去除无用列（即 temp 开头的列）
	for col in column_arr:
		if col.startswith('temp') :
			df.pop(col)
	# ------------------
	# 将数值列(字符串型)转成数值 
	float_column_arr = ['main_in','main_out','main_net_in','personal_in','personal_out','personal_net_in','total_fund_in']
	df = jxb.convert_df_type(df=df, xtype=float, column_arr=float_column_arr)
	# -------------------
	# 将单位转成标准单位
	for col in float_column_arr:
		df[col] *= 10000 			# 将万元为单位的转化成元为单位

	# 列按指定顺序排列
	df = jxb.sort_df_column(df=df, column_arr=cf.STOCK_COLUMN_ORDER_ARR)
	df = df.reset_index(drop=True)

	return df







# tencent data end
# ====================================





# -------------------------------------
# ifeng data start

def get_ifeng_k_data(code, index=False):
	"""
	说明：从凤凰网获取股票K线数据
	参数：code: 股票代码
	返回值：K线数据（df 格式）
	"""
	column_arr = [
		'date',				# 日期
		'open',				# 开盘价（元）
		'high', 			# 最高价（元）
		'close',			# 收盘价（元）
		'low', 				# 最低价（元）
		'volume', 			# 成交量（股）
		'price_change', 			# 涨跌额（元）
		'percent', 			# 涨跌幅（小数形式）
		'mean_price_5d', 	# 5 日均价（元）
		'mean_price_10d', 	# 10日均价（元）
		'mean_price_20d', 	# 20日均价（元）
		'mean_volume_5d', 	# 5日均量（股）
		'mean_volume_10d', 	# 10日均量（股）
		'mean_volume_20d', 	# 20日均量（股）
		'turnover', 		# 换手率（小数形式）
		]

	base_url = "http://api.finance.ifeng.com/akdaily/?code=%s&type=last"
	prefixed_code = cnstock.get_prefixed_code(code=code, index=index)
	url = base_url % (prefixed_code)
	
	# page_source = get_page_by_requests(url=url)	 		
	page_source = None
	page_source_arr = get_page([url])
	if page_source_arr is not None:
		page_source = page_source_arr[0]
	if page_source is None:
		return None
	
	s = json.loads(page_source) 		# 凤凰网返回的数据是 json 格式
	data_arr = s['record'] 				# 这是二维 list
	df = pd.DataFrame(data=data_arr,columns=column_arr)
	df['code'] = [code] * len(df) 		# 添加 code 列
	# 将这些列中的逗号替换为空，即去掉。否则这些列无法参与下面的类型转换
	for col in ['volume','mean_volume_5d','mean_volume_10d','mean_volume_20d']:
		df[col] = df[col].str.replace(',','') 			# 注意中间有个 str ，对于非 str 列必须转 str 才能成功执行 replace()
	# ------------------------------------	
	# 这些列的数据类型需要转成 float
	float_column_arr = ['open','high','close','low','volume','price_change','percent','mean_price_5d','mean_price_10d','mean_price_20d','mean_volume_5d','mean_volume_10d','mean_volume_20d','turnover']
	df = jxb.convert_df_type(df=df, xtype=float, column_arr=float_column_arr)
	# ------------------------------
	# 下面统一单位
	for col in ['percent','turnover']:
		df[col] /= 100 				# 将各类幅度转成小数，即真实幅度
	for col in ['volume','mean_volume_5d','mean_volume_10d','mean_volume_20d']:
		df[col] *= 100 				# 将各类成交量从手转成股
	# ----------------------------
	# 下面调整列和行顺序
	# 列排序
	df = jxb.sort_df_column(df=df, column_arr=cf.STOCK_COLUMN_ORDER_ARR)
	# 行排序
	df = df.sort_values(by=['date'], ascending=[True])
	df = df.reset_index(drop=True)

	return df







# ifeng data end
# =====================================






# ---------------------------------
# eastmoney data start


def get_all_code_from_eastmoney(wait_time=cf.WAIT_TIME):
	"""
	功能说明：本函数继续往下调用函数以返回所有股代码。
	Parameters
	----------
	wait_time : float, optional
		DESCRIPTION. The default is cf.WAIT_TIME.
		表示爬取时间间隔，
		本函数往下有两个分支可选，一个是调用 get_all_code_from_eastmoney1() ，这个不需要参数，直接返回数据，优先采用这个。
		另一个是 get_all_code_from_eastmoney2()，这个最终调用的是模拟浏览器方式，效率较低，容易给服务器造成压力，所以需要 wait_time
	Returns
	-------
	all_code_arr : df
		DESCRIPTION. 返回值是一个包含所有股票代码的 df，包含'code'和'name'两列

	"""
	all_code_df = get_all_code_from_eastmoney1()
	# all_code_arr = get_all_code_from_eastmoney2(wait_time=wait_time)
	
	return all_code_df





	

def get_all_code_from_eastmoney1():
	"""
	说明：从东方财富网爬取所有股票代码
	参数：无
	返回值：df 形式的股票代码(包含两个字段，分别是 'name','code')
	"""
	result_arr = get_total_page_from_eastmoney()
	if result_arr is None:
		return None
	
	[total_page, all_code_df] = result_arr
	if total_page <= 1:
		return all_code_df

	base_url = cf.URL_DICT['EASTMONEY5_PART1']
	url_arr = []
	for page_num in range(2, total_page+1):
		url = base_url % (page_num)
		url = url + cf.URL_DICT['EASTMONEY5_PART2']		
		url_arr.append(url)
	
	#page_source_arr = get_page_by_gevent(url_arr=url_arr)
	page_source_arr = get_page(url_arr=url_arr)
	if page_source_arr is None:
		return None
	
	code_arr = []
	# 下面这个 for , 从上面最早返回的协程中提取 value
	for page_source in page_source_arr:
		if page_source is None:
			continue
		# ----------------
		reg = '{.*}}' 			# 提取数据用的正则
		arr = re.findall(reg, page_source)
		if len(arr) == 0:
			continue
		
		data_dict = json.loads(arr[0])
		for sub_arr in data_dict['data']['diff']:
			code = sub_arr['f12']
			name = sub_arr['f14']
			code_arr.append([code,name])
	
	#all_code_arr.sort(reverse=False)
	if len(code_arr) > 0:
		code_df = pd.DataFrame(data=code_arr,columns=['code','name'])
		all_code_df = pd.concat([all_code_df,code_df])
	
	return all_code_df









def get_total_page_from_eastmoney():
	"""
	说明：从东方财富网主力排名这一节爬取第 1 页所有股票代码（每页约50行）及总页数
	参数：无
	返回值：是一个 list，包含两个元素，第一个元素是总页数(int类型)，第2个元素是一个df，存放的是主力排名节首页的股票代码
	"""
	result_arr = []			# 存放总页码及首页股票代码子df
	total_page = 1 			# 预设东财主力排名表格总页数为 1
	code_arr = [] 			# 存放东财主力排名节第1页的股票代码
	
	base_url = cf.URL_DICT['EASTMONEY5_PART1']
	url_arr = []
	for page_num in range(1,2):
		url = base_url % (page_num)
		url = url + cf.URL_DICT['EASTMONEY5_PART2']		
		url_arr.append(url)
	
	#page_source_arr = get_page_by_gevent(url_arr=url_arr)
	page_source_arr = get_page(url_arr=url_arr)
	if page_source_arr is None:
		return None

	total_row = 0 			# 预设总行数为0
	#total_page = 0 			# 预设总页数为0
	for page_source in page_source_arr:
		if page_source is None:
			continue
		# ----------------
		reg = '{.*}}' 			# 提取数据用的正则
		arr = re.findall(reg, page_source)
		if len(arr) == 0:
			continue
		
		data_dict = json.loads(arr[0])
		total_row = int(data_dict['data']['total'])
		# total_page = int(total_row / 50) + 1

		for sub_arr in data_dict['data']['diff']:
			code = sub_arr['f12']
			name = sub_arr['f14']
			code_arr.append([code,name])
	
	if len(code_arr) > 0:
		total_page = int(total_row/len(code_arr)) + 1
		
	#code_arr.sort(reverse=False)
	code_df = pd.DataFrame(data=code_arr,columns=['code','name'])
	result_arr = [total_page, code_df]
	
	return result_arr










	

def get_all_code_from_eastmoney2(wait_time=cf.WAIT_TIME):
	"""
	说明：从东方财富网爬取所有股票代码
	参数：wait_time: 相邻两次调用间隔时间，这是为应对反爬考虑。用户可以指定一个间隔时间，默认值为0，即全速前进。
	返回值：list 形式的股票代码
	"""
	pass
	
	#all_df = get_eastmoney_realtime_stock_data(wait_time=wait_time)
	all_df = get_eastmoney_main_rank(wait_time=wait_time)
	all_code_arr = all_df.code.tolist() 
	#all_code_arr = list(set(list(all_df.code)))
	all_code_arr.sort(reverse=False)

	return all_code_arr








def get_eastmoney_realtime_stock_data(wait_time=cf.WAIT_TIME):
	"""
	说明：从东方财富网爬取所有股的实时数据。注意：本接口拿数据比较耗时，不建议用它做实时行情。
	参数：wait_time: 相邻两次调用间隔时间，这是为应对反爬考虑。用户可以指定一个间隔时间，默认值为0.1，即全速前进。	
	返回值：df 格式的所有股的实时数据
	"""
	# 指定用 phantomjs 浏览器去打开网页
	#browser_driver = webdriver.PhantomJS(browser, service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any']) 		
	#browser_driver = webdriver.PhantomJS(browser) 	
	# 东财行情 URL 
	print(jxb.get_current_function_name(),' 请注意，每次调用本函数约需 90 秒才能返回所有股票代码。建议不要频繁调用本函数，以免给网站造成压力。')

	anchor = "#hs_a_board"				# 网页中的锚点
	url = cf.URL_DICT['EASTMONEY'] + anchor

	browser_driver = get_browser_driver()
	if browser_driver is None:
		return None
	# 打开 url 所指页面，返回的页面html代码（含数据）在 browser_driver 这个对象中，并且已经解码过了（浏览器自动解码）是纯文本（字符串）形式
	browser_driver.get(url)

	page_count = 1 			# 页码计数器
	all_df = None
	while True:
		print('正在爬第 %d 页...' % (page_count))
		#print('#',end='') 		# 爬虫进度符
		# 调用 driver 对象的属性 page_source 来提取网页源码及数据（注：浏览器返回的对象已经解码成纯文本（字符串）数据了）
		page_source = browser_driver.page_source
		page_source = page_source.replace('&nbsp;','') 			# 去除 &nbsp;
		#page_source = page_source.decode('utf-8') 				# 这句要注释掉， 因为用模拟浏览器方式返回的数据已经是用 utf-8 decode 过了，成了 str 形式，不能重复做 decode()
		#soup = bs4.BeautifulSoup(page_source, "lxml") 			# 准备用 lxml 解析网页源码内容 page_source

		table_arr = get_table(page_source=page_source) 		# 东财网返回的数据只有一个 table
		if table_arr is not None and len(table_arr) >= 1:
			table_df = table_arr[0]
			table = jxb.df2list(df=table_df)
			table = table[1:] 			# 从第 1 行开始取（即去掉第0行，因为0行是表头）
			df = eastmoney_table2df(table=table)
	
		if all_df is None:
			all_df = df
		else:
			if df is not None:
				all_df = pd.concat([all_df,df])
		# ------------
		# 抓几页
		if page_count >= 5:
			pass
			break 			# 如果测试的话，打开这个 break，这样只爬5页就停下来，防止爬200多页耗费很多时间
		page_count += 1
		# ------------------
		# soup.find_all() 将返回一个 list,  list 中的元素都是 soup 对象，可以用 .get_text() 方法提取 html 首尾标记之间的内容
		# if len(soup.find_all(name='a', attrs='next paginate_button')) > 0 and len(soup.find_all(name='a', attrs='next paginate_button disabled')) == 0:
		# 下面这个 if 表示在 browser_driver.find_element_by_xpath('//a[contains(text(),"下一页")]').get_attribute(name='class') （这一长串调用后最终返回的是字符串文本）中查找有没 disabled 这个词，
		# 根据事先分析得知，若 'disabled' 出现在“下一页”所在的 <a> 的 class 中的话，则表示已经是最后一页了，此时要停止翻页
		if 'disabled' in browser_driver.find_element_by_xpath('//a[contains(text(),"下一页")]').get_attribute(name='class'):
			break
		else:
			# 下面继续翻页	
			time.sleep(wait_time) 			# 休息一个 wait_time ，防止爬的过快遭遇网站反爬
			# 下面两句点击都是正确的，选一句执行即可（后来实践发现：by_xpath 比 by_link 快得多，所以采用 by_xpath）
			#browser_driver.find_element_by_link_text('下一页').click() 					# find_element_by_link_text() 定位方式只能定位 <a> </a> 之间的文本			
			#browser_driver.find_element_by_xpath("//a[@class='next paginate_button']").click() 		# 点击“下一页”。由于每一页需要在上一页基础上点击下一页才能继续，所以很难用异步方式爬取
			para = '''.find_element_by_xpath('//a[@class="next paginate_button"]').click()''' 					# find_element_by_link_text() 定位方式只能定位 <a> </a> 之间的文本
			result_arr = jxb.retry_command(command=browser_driver, para=para, wait_time=wait_time)
			if result_arr is not None:
				[browser_driver,result] = result_arr
				continue
			else:
				break

	if all_df is not None:
		all_df = all_df.drop_duplicates()		# 去除重复记录
		all_df = all_df.sort_values(by=['code'], ascending=True)
		all_df = all_df.reset_index(drop=True)

	# -------------------
	# 使用结束要关闭和退出 browser_driver 对象
	browser_driver.close()
	browser_driver.quit()

	return all_df








def eastmoney_table2df(table=None, column_arr=None):
	"""
	说明：本函数的作用是将来自eastmoney.com 的 <table> 行情数据转成 df
	参数：table: 爬自东财的数据表，必须是个二维表，每个元素是一维 list，代表一行数据; column_arr: 是用于构造 df 的列头
	返回值：df
	"""
	if table is None:
		print('请传入来自东财（http://quote.eastmoney.com/center/gridlist.html#hs_a_board）的二维数据表，每个元素是一维 list，代表一行数据')
		return None

	if column_arr is None:
		column_arr = ['code','name','price','percent','price_change','volume','amount','amplitude','high','low','open','last_close','liangbi','turnover','pe','pb']

	table_arr = []
	for row_arr in table:		
		row_arr = row_arr[1:3] + row_arr[6:] 		# 东财有几个数据列是没用的，必须去掉
		table_arr.append(row_arr)

	table_df = None
	if len(table_arr) > 0:
		table_df = pd.DataFrame(data=table_arr, columns=column_arr)
		# -------------------------
		# 下面开始处理 table 中的一些列
		# 1. 先去除这几列的百分号，转化成纯数字，方便计算
		for col in ['percent','amplitude','turnover']:
			table_df[col] = table_df[col].replace('[%]','',regex=True) 						# 把这 3 列中的 % 去掉，并且除以100
			table_df= jxb.convert_df_type(df=table_df, xtype=float, column_arr=[col]) 			# 注意：这个函数会将数字列中非数字的域填 0 处理！！！
			#table_df[col] = table_df[col].astype(dtype=float) 									# 把字符串转成 float 才能做数学运算
			table_df[col] /= 100

		# -------------------------------------
		# 2. 再去除 volume 列的中文单位（万手或亿手），转化成股
		for col in ['volume','amount']:
			# 分拣
			df1 = table_df[~(table_df[col].str.contains('万|亿'))] 		# 表示在 table_df.volume列中选取不包含“万”字且不包含“亿”字的记录
			df2 = table_df[(table_df[col].str.contains('万'))]  			# 表示在 table_df.volume列中选取只包含“万”字的记录
			df3 = table_df[(table_df[col].str.contains('亿'))]  			# 表示在 table_df.volume列中选取只包含“亿”字的记录
			# 替换
			df2[col] = df2[col].replace('[万]', '', regex=True) 		
			df3[col] = df3[col].replace('[亿]', '', regex=True) 		
			# 转化成数值
			df1 = jxb.convert_df_type(df=df1, column_arr=[col])
			df2 = jxb.convert_df_type(df=df2, column_arr=[col])
			df3 = jxb.convert_df_type(df=df3, column_arr=[col])
			# 转成常规单位
			df1[col] *= 1
			df2[col] *= 10000
			df3[col] *= 100000000

			table_df = pd.concat([df1,df2,df3])

		table_df['volume'] = table_df['volume'].astype(dtype=float) * 100 			# 把以手为单位的成交量转换成股
		# ---------------------------------------
		# 下面对 table_df 的数值列明确转换为数值
		number_column_arr = column_arr[2:]
		table_df = jxb.convert_df_type(df=table_df, xtype=float, column_arr=number_column_arr) 	# 注意：这个函数会将数字列中非数字的域填 0 处理！！！

	return table_df







def get_eastmoney_main_rank(wait_time=cf.WAIT_TIME):
	"""
	说明：从东方财富网爬取所有股主力排名。注意：本接口拿数据比较耗时。
	参数：wait_time: 相邻两次调用间隔时间，这是为应对反爬考虑。用户可以指定一个间隔时间，默认值为0.1，即全速前进。
	返回值：df 格式的所有股的实时数据
	"""
	# 指定用 phantomjs 浏览器去打开网页
	#browser_driver = webdriver.PhantomJS(browser, service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any']) 		
	#browser_driver = webdriver.PhantomJS(browser) 	
	# 东财行情 URL 
	print(jxb.get_current_function_name(),' 请注意，每次调用本函数需要较长时间才能爬回结果。建议不要频繁调用本函数，以免给网站造成压力。')

	anchor = ""				# 网页中的锚点
	url = cf.URL_DICT['EASTMONEY3'] + anchor

	browser_driver = get_browser_driver()
	if browser_driver is None:
		return None
	# 打开 url 所指页面，返回的页面html代码（含数据）在 browser_driver 这个对象中，并且已经解码过了（浏览器自动解码）是纯文本（字符串）形式
	browser_driver.get(url)
	#page_source = browser_driver.page_source
	#browser_driver.find_element_by_xpath("//*[contains(text(),'沪深A股')]").click() 		# 点击沪深A股标签
	page_count = 1 			# 页码计数器
	all_df = None
	while True:
		print('正在爬第 %d 页...' % (page_count))
		#print('#',end='') 		# 爬虫进度符
		# 调用 driver 对象的属性 page_source 来提取网页源码及数据（注：浏览器返回的对象已经解码成纯文本（字符串）数据了）
		page_source = browser_driver.page_source
		page_source = page_source.replace('&nbsp;','') 			# 去除 &nbsp;		
		#page_source = page_source.decode('utf-8') 				# 这句要注释掉， 因为用模拟浏览器方式返回的数据已经是用 utf-8 decode 过了，成了 str 形式，不能重复做 decode()
		#soup = bs4.BeautifulSoup(page_source, "lxml") 			# 准备用 lxml 解析网页源码内容 page_source

		table_arr = get_table(page_source=page_source) 		# 东财网返回的数据有两个 <table>，第1个 table 是表头，第2个table 才是真正的数据。
		if table_arr is not None and len(table_arr) >= 2:
			df = table_arr[1] 			# table_arr 中的元素是 df, 分析返回的数据后发现第0个元素是没用的，第1个才有用
			df = df.loc[:,[1,2]] 		# 只取第 1，2 列（分别是股票代码和名称），其他列的信息不要
			df = df.reset_index(drop=True)
			df = df.drop(labels=range(0,2),axis=0) 		# 删除 0到2（含0不含2）之间的行，axis=0 表示按行删。这两行是没用的数据

		if all_df is None:
			all_df = df
		else:
			if df is not None:
				all_df = pd.concat([all_df,df])
		# ------------
		# 抓几页
		if page_count >= 5:
			pass
			break 			# 如果测试的话，打开这个 break，这样只爬5页就停下来，防止爬200多页耗费很多时间
		page_count += 1
		# ------------------
		# soup.find_all() 将返回一个 list,  list 中的元素都是 soup 对象，可以用 .get_text() 方法提取 html 首尾标记之间的内容
		# if len(soup.find_all(name='a', text='下一页')) > 0 :
		if browser_driver.find_element_by_xpath("//div[@class='pagerbox']").text.find('下一页') >= 0:
			time.sleep(wait_time)
			# 下面这两句点击都是正确的，选一句即可（后经测试，第2句by_xpath 写法比第1句 by_link_text 要快得多，所以采用第2句）
			#browser_driver.find_element_by_link_text('下一页').click() 			# find_element_by_link_text() 定位方式只能定位 <a> </a> 之间的文本
			#browser_driver.find_element_by_xpath("//a[contains(text(),'下一页')]").click() 		# 点击“下一页”。由于每一页需要在上一页基础上点击下一页才能继续，所以很难用异步方式爬取
			para = '''.find_element_by_xpath("//a[contains(text(),'下一页')]").click()''' 			# 点击“下一页”。
			result_arr = jxb.retry_command(command=browser_driver, para=para, wait_time=wait_time)
			if result_arr is not None:
				[browser_driver,result] = result_arr
				continue
			else:
				break
		else:
			break

	if all_df is not None:
		all_df.columns = ['code','name']
		# 从 all_df 中提取以下4类股票
		# 下面两句（即 contains 和 starswith）表达方式不同，但效果是相同的，所以只选一句即可。
		#stock_60_df = all_df[all_df['code'].str.contains('^' + stock_60_rule_dict['CODE_TYPE'])] 		# 获取 60 开头的股票行，stock_60_rule_dict['CODE_TYPE'] 是一个正则表达式，contains() 也能接受的，它也可以接受字符串作为参数
		stock_60_df = all_df[all_df['code'].str.startswith(stock_60_rule_dict['CODE_TYPE'])] 		# 获取 60 开头的股票行，stock_60_rule_dict['CODE_TYPE'] 是一个正则表达式，contains() 也能接受的，它也可以接受字符串作为参数
		stock_688_df = all_df[all_df['code'].str.startswith(stock_688_rule_dict['CODE_TYPE'])] 		# 获取 688 开头的股票行，stock_688_rule_dict['CODE_TYPE'] 是一个正则表达式，contains() 也能接受的，它也可以接受字符串作为参数
		stock_00_df = all_df[all_df['code'].str.startswith(stock_00_rule_dict['CODE_TYPE'])] 		# 获取 00 开头的股票行，stock_00_rule_dict['CODE_TYPE'] 是一个正则表达式，contains() 也能接受的，它也可以接受字符串作为参数
		stock_30_df = all_df[all_df['code'].str.startswith(stock_30_rule_dict['CODE_TYPE'])] 		# 获取 300 开头的股票行，stock_30_rule_dict['CODE_TYPE'] 是一个正则表达式，contains() 也能接受的，它也可以接受字符串作为参数
		# 把 4 类股票合在一起
		all_df = pd.concat([stock_60_df,stock_688_df,stock_00_df,stock_30_df])
		all_df = all_df.drop_duplicates()		# 去除重复记录		
		all_df = all_df.sort_values(by=['code'], ascending=True)
		all_df = all_df.reset_index(drop=True)

	# -------------------
	# 使用结束要关闭和退出 browser_driver 对象
	browser_driver.close()
	browser_driver.quit()

	return all_df








def get_stock_price_volume_distribution(code, xbegin, xend=None):
	"""
	功能说明：根据传入的股票代码和日期范围，获取筹码分布数据
	参数：
		code: str型，必填。
			说明：股票代码。
		xbegin: str型（格式 yyyy-mm-dd）或python 日期型，必填。
			说明：统计筹码分布的起始日期
		xend: str型（格式 yyyy-mm-dd）或python 日期型，可选，默认值: None。
			说明：统计筹码分布的结束日期，若没传入，则和 xbegin 取相同日期。
			表示 xbegin 这一天的筹码分布。
	返回值：	筹码分布数据（df 格式）
	"""
	code = str(code)
	# 下面对传入的股票代码加市场前缀
	#code_arr = get_prefixed_code_arr(code_arr=[code])
	code_arr = cnstock.get_prefixed_code_arr(code_arr=[code])
	xbegin = str(xbegin)
	if xend is None:
		xend = xbegin
		
	base_url = cf.URL_DICT['SINA2']
	url = base_url % (code_arr[0],xbegin,xend)
	
	page_source_arr = get_page(url_arr=[url])
	page_source = page_source_arr[0]
	# 下面根据给定的页面源码，返回一个 list，其中的每个元素是个 df，对应页面中的一个 table
	# 本例中页面恰好只有一个 table, 即 table_arr[0], 它已经被转成了 df 格式
	table_arr = get_table(page_source=page_source)
	if table_arr is None or len(table_arr) == 0:
		print('错误！没有数据')
		return None
	
	df = table_arr[0]
	# 根据对返回的数据分析，从 df 中选取第2行（即行标1）开始到结束，列的话选1，3，5列
	df = df.loc[1:,[1,3,5]]
	
	# 对返回的数据定义列名
	column_arr = ['price','volume','percent']
	# 给返回的数据添加列名
	df.columns = column_arr
	# ----------------------
	# 将第 price 和 volume 列的百分号去掉，并将值转成小数
	for col in ['price','volume']:	
		df[col] = df[col].replace('[,]','',regex=True)
	# 将第percent列的百分号去掉，并将值转成小数
	df['percent'] = df['percent'].replace('[%]','',regex=True)
	
	# 将 price 和 percent 列值转化为 float 型
	df = jxb.convert_df_type(df=df, xtype=float, column_arr=['price','percent'])
	df['percent'] /= 100 		# 将 percent 转成真实小数
	# 将 volume 列值转化为 int 型
	df = jxb.convert_df_type(df=df, xtype=int, column_arr=['volume'])
	# 按股价从高到低排序
	df = df.sort_values(by=['price'], ascending=[False])
	# 对行号重新按自增方式编排
	df = df.reset_index(drop=True)
	
	return df
	
	
	
	


	
	
	

# eastmoney data end
# ==================================




# private interface for inner use end
# ===========================================
# ==========================================




# 以下代码仅用于测试，测试完删掉。
if __name__ == '__main__':
	
	code_arr = ['300101']
	
	df = get_distribution('300101', xbegin='2022-01-11')
	
	