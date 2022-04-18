#coding=utf-8

"""
作者：xjxfly
邮箱：xjxfly@qq.com
说明：
此脚本为自定义的全局常量

"""
###########################

# 下面这个常量 MONKEY_PATCH_ALL 表示是否使采用 gevent 的 monkey.patch_all() 给本包打猴子补丁以让同步库变成异步库
# 默认 False，表示不打补丁。因为测试发现打猴子补丁后在 ipython 下运行不正常，也担心出其他问题，
# 所以这里默认设 False，用户若确定需要使用 monkey.patch_all()，将下面这个常量改为 True，并重新 install 本包
MONKEY_PATCH_ALL = False

# 爬虫要访问的网站
URL_DICT = {
	"EASTMONEY":"http://quote.eastmoney.com/center/gridlist.html", 			# 沪深行情数据
	"EASTMONEY2":"http://quote.eastmoney.com/center/gridlist2.html",
	"EASTMONEY3":"http://data.eastmoney.com/zjlx/list.html", 				# 主力排名
	# 沪深主力排名数据，从这里取all_code
	"EASTMONEY5_PART1":"http://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112305285492333661328_1615304191970&fid=f184&po=1&pz=50&pn=%d",
	"EASTMONEY5_PART2":"&np=1&fltt=2&invt=2&fields=f2%2Cf3%2Cf12%2Cf13%2Cf14%2Cf62%2Cf184%2Cf225%2Cf165%2Cf263%2Cf109%2Cf175%2Cf264%2Cf160%2Cf100%2Cf124%2Cf265&ut=b2884a393a59ad64002292a3e90d46a5&fs=m%3A0%2Bt%3A6%2Bf%3A!2%2Cm%3A0%2Bt%3A13%2Bf%3A!2%2Cm%3A0%2Bt%3A80%2Bf%3A!2%2Cm%3A1%2Bt%3A2%2Bf%3A!2%2Cm%3A1%2Bt%3A23%2Bf%3A!2%2Cm%3A0%2Bt%3A7%2Bf%3A!2%2Cm%3A1%2Bt%3A3%2Bf%3A!2",
	
	# ----------------------
	# 筹码分布
	"SINA2":"http://market.finance.sina.com.cn/pricehis.php?symbol=%s&startdate=%s&enddate=%s",
	# 美股行情
	#"SINA3":"https://stock.finance.sina.com.cn/usstock/api/jsonp.php/IO.XSRV2.CallbackList['f0j3ltzVzdo2Fo4p']/US_CategoryService.getList?page=%d&num=600&sort=&asc=0&market=&id="
	"SINA3":"https://stock.finance.sina.com.cn/usstock/api/jsonp.php/IO.XSRV2.CallbackList/US_CategoryService.getList?page=%d&num=600&sort=&asc=0&market=&id="
	
	}



WAIT_TIME = 0.1 		# 定义爬虫爬取间隔时间，用户可通过某些调用接口传入参数来修改这个间隔时间

PUBLIC_KEY = '-----BEGIN RSA PUBLIC KEY-----\nMIGJAoGBAIA1iCmKW3gTYunJq/kKx7WIel0Wfec85kZZoFwzn8wG8js1a8lYF75r\nkmVhbS52nhlIGzh39yfRflH+kUAjSKtR0gjgCUrkPkLpFRLvwv52q56uulIW+3Rg\nIYYhr+6gS4wMgUVRK3OL2FRCLLWxWlTxRHHpuk3rDRvs6H5jYwCVAgMBAAE=\n-----END RSA PUBLIC KEY-----\n'

PRIVATE_KEY = '-----BEGIN RSA PRIVATE KEY-----\nMIICXwIBAAKBgQCANYgpilt4E2Lpyav5Cse1iHpdFn3nPOZGWaBcM5/MBvI7NWvJ\nWBe+a5JlYW0udp4ZSBs4d/cn0X5R/pFAI0irUdII4AlK5D5C6RUS78L+dquerrpS\nFvt0YCGGIa/uoEuMDIFFUStzi9hUQiy1sVpU8URx6bpN6w0b7Oh+Y2MAlQIDAQAB\nAoGAHnka0QzSqtqowvqtRndaenpi4ydKa6Dc9tGsvN2EWME55/rNkMDAfAEjfbdH\ndSi6cTXjSmuxMiSoCqMgAmtSFpaZEfjUULS5ngUmKjL0XO9aYYytitbWBQ9G3nvw\nJqsGfixkfaA1LhvyBPNkRR9oe49GZXCVZMgqp6UlkqsnGCECRQDEGfDUENxL/iBw\nQKmTF7y7WY79DFSsLKBIp1hZYJn7vsluOC9z7lOPYwpKB6MVmlGpfy8Qq1+PQMNj\nV9X5hFLvkI1UOQI9AKdeybyDATc4jnQJPizLYHE/BdFalAyQs0mXcebs5aZB3/Mj\n8W3yCAbSFsNFENxYGeexJM0ik3226WtnPQJECb7kShXAbQJnKEz+YHIIjiMISSko\nuBnLqXCvoll7rZgwuIqQSSmp+3FHnKA+iZ9Ouaa5dxGdQShNzY0a9DiQSpmbfHkC\nPGbDdVwwl5t/N0AZuLoqOVHvHzRWyBYa9moV+ZKPG8YEJmwUQpV+CN2fOui0TFDu\nKyGuC2mEdEi4+QLABQJEIFniajsMdiHAyRvBxj4+ILrFSPNXaHqWi/PdmI97twXJ\nR28hcrf1qa8rZKrMVXJw/lyeN55fGorQAyYlTsHYLbQGQeY=\n-----END RSA PRIVATE KEY-----\n'
# ---------------------------------------

# 定义股票列名顺序，为了使所有行情源返回的数据其字段保持相同的顺序排列，请不要改变下面 list 中的元素顺序，所有行情返回的数据最终都将参照下面这个 list 对列进行排序。（下列中的元素可随意增减或添加程序中不存在的元素，或调整顺序等，都不会导致程序出错）
STOCK_COLUMN_ORDER_ARR =  [
	'date', 					# 日期
	'time', 					# 时间
	'code', 					# 证券代码
	'name', 					# 证券名称
	'cname', 					# 证券名称（中文）
	'last_close', 				# 昨收价（元）
	'open', 					# 开盘价（元）
	'high', 					# 最高价（元）
	'low', 						# 最低价（元）
	'price', 					# 市价（元）
	'average_price', 			# 均价（元）
	'max_price', 				# 涨停价（元）
	'min_price', 				# 跌停价（元）
	'close', 					# 收盘价（元）
	'volume', 					# 成交量（股）
	'amount', 					# 成交额（元）
	'ask5_price', 				# 卖五价（元）
	'ask5_volume', 				# 卖五量（股）
	'ask4_price', 				# 卖四价（元）
	'ask4_volume', 				# 卖四量（股）
	'ask3_price', 				# 卖三价（元）
	'ask3_volume', 				# 卖三量（股）
	'ask2_price', 				# 卖二价（元）
	'ask2_volume', 				# 卖二量（股）
	'ask1_price', 				# 卖一价（元）
	'ask1_volume', 				# 卖一量（股）
	'bid1_price', 				# 买一价（元）
	'bid1_volume', 				# 买一量（股）
	'bid2_price', 				# 买二价（元）
	'bid2_volume', 				# 买二量（股）
	'bid3_price', 				# 买三价（元）
	'bid3_volume', 				# 买三量（股）
	'bid4_price', 				# 买四价（元）
	'bid4_volume', 				# 买四量（股）
	'bid5_price', 				# 买五价（元）
	'bid5_volume', 				# 买五量（股）
	'price_change', 					# 涨跌额（元）
	'percent', 					# 涨幅（小数表示真实幅度）
	'amplitude', 				# 振幅（小数表示真实幅度）
	'turnover', 				# 换手率（小数表示真实幅度）
	'circulation_value', 		# 流通值（元）
	'total_value', 				# 总市值（元）
	'pe_static', 				# 静态市盈率
	'pe_dynamic', 				# 动态市盈率
	'pe_ttm', 					# 滚动市盈率
	'pb', 						# 市净率
	'liangbi' 					# 量比
	]



# ==============================




