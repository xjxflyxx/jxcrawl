




get_all_code(wait_time=0.1, source='eastmoney')
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
get_all_code_df(wait_time=0.1, source='eastmoney')
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
get_api_list()
功能说明：本函数仅仅用于返回可用接口列表，不在列表中列出的函数或接口等请不要调用，他们一般在内部实现使用，未来可能会改名或调整！！
 
Returns
-------
返回值：可用接口, list形式
get_distribution(code, xbegin, xend=None, category='stock', market='hushen')
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
返回值：    筹码分布数据（df 格式）
get_fund_flow(code, index=False, source='tencent', catetory='stock', market='hushen')
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
get_k_data(code, xbegin, xend, index=False)
功能说明：根据传入的股票代码和日期范围获取相应的K线数据，这和上面的 get_data(xtype='k') 是一样的。
参数：
        code: 股票代码，str 型
        xbegin: 起始日期，str 型或python 日期型
        xend: 结束日期，str型或 python 日期型
返回值：DF形式的K线数据
get_live_data(code_arr, index=False, source='tencent')
功能说明：根据传入的股票代码 list ，获取相应的实时数据返回
参数：
        code_arr: 股票代码 list, 每个元素是str 型的股票代码
        index: 表示传入的 code_arr 是否指数，默认 False
        source: 表示从哪个源获取实时数据，可取值'sina','netease','qq'，不区分大小写
返回值：df 形式的实时 tick 数据。
get_page(url_arr, asyn=False, by='requests', xcount=None)
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
get_table(page_source, separator='||')
功能说明：从网页源码中提取表格数据返回
参数：
        page_source: str型，必填。
        说明：该参数要指向网页源码（可以是通过 requests 或 selenium + phantomjs等爬到的网页源码）；
        注意：页面源码必须是已经 decode() 过的纯文本（字符串形式），不能是字节流形式；
返回值：table_arr, list型, 其中每个元素是对应网页中一个 <table> (df格式)。若页面不是 str型则返回 None
get_usa_live_data()
说明：从新浪获取美股实时行情
参数：无
返回值：美股所有股行情，df格式
is_trade_date(category='stock', market='hushen')
功能说明：判断今天是否交易日。该函数通过从获取指数（上证综指）的实时数据中提取日期，以判断今天是否交易日。
        注意：只有在开盘后调用才有用，所以建议在 9：15 后调用本函数，否则不准。
参数：无 
返回值：bool型，交易日返回 True, 非交易日返回 False. 无法判断返回 None.
make_header()
功能说明：构造一个 http 请求头返回
save_page(page_source, filename, mode='a')
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
