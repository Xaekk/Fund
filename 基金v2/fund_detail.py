from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from tqdm import tqdm
from chromedriver import web_driver
import datetime
import threading
import time
from browser_pool import browser_pool
#============= Configer =======================
bar_lengh = 60

history_thread_amount = 10
#=============== Tools ========================
def wait_action(browser, name=None):
    if name == None: name = ''
    else: name = '['+str(name)+']'
    print(name+'Waiting for Reflesh ...')
    while(BeautifulSoup(browser.page_source, "html.parser").get_text().find('长时间不更新') != -1):
        ''' Waiting for Reflesh '''
        pass
    print(name+'Reflesh Done.')
#============== Function ======================
def funds(data_array):
    '''Getting Funds'''
    print('Getting Funds ...')
    url = "http://fund.eastmoney.com/data/fundranking.html#tall;pn10000"
    browser = browser_pool.acquire()
    print('Getting page ==> ', url)
    browser.get(url)

    wait_action(browser)

    trs = BeautifulSoup(browser.page_source, "html.parser").find(id='dbtable').tbody.findAll('tr')
    browser.release()
    #Scope
    for tr in tqdm(trs, ncols=bar_lengh):
    ##for tr in trs[:20]:
        tds = tr.findAll('td')
        detail_map = {}
        detail_map['基金代码'] = tds[2].get_text().replace(' ', '')
        detail_map['基金简称'] = tds[3].get_text().replace(' ', '')
        try:
            detail_map['日增长率'] = float(tds[7].get_text().replace(' ', '').replace('%', ''))
            detail_map['近1周'] = float(tds[8].get_text().replace(' ', '').replace('%', ''))
            detail_map['近1月'] = float(tds[9].get_text().replace(' ', '').replace('%', ''))
            detail_map['近3月'] = float(tds[10].get_text().replace(' ', '').replace('%', ''))
        except ValueError:
            continue
        try:
            detail_map['近6月'] = float(tds[11].get_text().replace('---', '').replace(' ', '').replace('%', ''))
        except ValueError:
            detail_map['近6月'] = 0
        try:
            detail_map['近1年'] = float(tds[12].get_text().replace('---', '').replace(' ', '').replace('%', ''))
        except ValueError:
            detail_map['近1年'] = 0    
        try:
            detail_map['近2年'] = float(tds[13].get_text().replace('---', '').replace(' ', '').replace('%', ''))
        except ValueError:
            detail_map['近2年'] = 0
        try:
            detail_map['近3年'] = float(tds[14].get_text().replace('---', '').replace(' ', '').replace('%', ''))
        except ValueError:
            detail_map['近3年'] = 0
        try:
            detail_map['今年来'] = float(tds[15].get_text().replace('---', '').replace(' ', '').replace('%', ''))
        except ValueError:
            detail_map['今年来'] = 0
        try:
            detail_map['成立来'] = float(tds[16].get_text().replace('---', '').replace(' ', '').replace('%', ''))
        except ValueError:
            detail_map['成立来'] = 0
        try:
            detail_map['手续费'] = float(tds[18].get_text().replace('---', '').replace(' ', '').replace('%', ''))
        except ValueError:
            detail_map['手续费'] = 100
            
        data_array.append(detail_map)

def add_history(data_array, date=None, latest_days=30):
    '''Add Funds History Rate'''
    print('Getting Funds History Rate ...')
    for fund in data_array:
        fund['历史记录'] = []
        fund['最近三天历史记录'] = []

    if date == None:
        date = datetime.datetime.now()

    time_clock = time.clock()
    
    lock = threading.Lock()
    threads = []
    latest_days_ = 0
    account = 0
    while latest_days_ < latest_days:
        account += 1        

        if account <= history_thread_amount:
            latest_days_ += 1
            latest_history = False if latest_days_>4 else True
            latest_history = False
            thread = threading.Thread(target=add_history_data, args=(data_array, date, lock, latest_history))
            thread.start()
            threads.append(thread)
            date = date - datetime.timedelta(days=1)
        else:
            account = 0
            for thread in threads:
                thread.join()
            threads = []
    # 不能整除10个时
    for thread in threads:
        thread.join()

    print('总耗时:{:.2f}s'.format(time.clock()-time_clock))
    browser_pool.clean()

def add_history_data(data_array, date, lock, latest_history=False):
    zero_amount = 0
    date_start = date - datetime.timedelta(days=1)
    date_end = date
    date_start_str = (str(date_start.year) if date_start.year >= 10 else '0' + str(date_start.year)) + (
        str(date_start.month) if date_start.month >= 10 else '0' + str(date_start.month)) + (
                         str(date_start.day) if date_start.day >= 10 else '0' + str(date_start.day))
    date_end_str = (str(date_end.year) if date_end.year >= 10 else '0' + str(date_end.year)) + (
        str(date_end.month) if date_end.month >= 10 else '0' + str(date_end.month)) + (
                       str(date_end.day) if date_end.day >= 10 else '0' + str(date_end.day))
    url = "http://fund.eastmoney.com/data/fundranking.html#tall;pn10000;qsd%s;qed%s;" % (
        date_start_str, date_end_str)
    # TODO: 用 浏览器池
    browser = browser_pool.acquire()
    print('Getting History : %s-%s-%s\nGetting page ==>%s' % (str(date.year) if date.year >= 10 else '0' + str(date.year),
                                          str(date.month) if date.month >= 10 else '0' + str(date.month),
                                          str(date.day) if date.day >= 10 else '0' + str(date.day),
                                                            url))
    browser.get(url)

    soup = BeautifulSoup(browser.page_source, "html.parser")
    #TODO: 用 浏览器池
    browser.release()
    trs = soup.find(id='dbtable').tbody.findAll('tr')
    lock.acquire()
    try:
        print('Add History : %s-%s-%s' % (str(date.year) if date.year >= 10 else '0' + str(date.year),
                                              str(date.month) if date.month >= 10 else '0' + str(date.month),
                                              str(date.day) if date.day >= 10 else '0' + str(date.day)))
        # Scope
        pbar = tqdm(total=len(trs), ncols=bar_lengh)
        for tr in trs:
            tds = tr.findAll('td')

            code = tds[2].get_text().replace(' ', '')
            try:
                rate = float(tds[17].get_text().replace(' ', '').replace('%', ''))
            except ValueError:
                rate = 0.

            if rate == 0.:
                zero_amount += 1

            for fund in data_array:
                if fund['基金代码'] == code:
                    if latest_history:
                        fund['最近三天历史记录'].append(rate)
                    else:
                        fund['历史记录'].append(rate)
            pbar.update(1)
        pbar.close()
        if zero_amount > len(data_array) / 2:
            for fund in data_array:
                fund['历史记录'] = fund['历史记录'][:-1]
            print('被清空[历史记录]日期 : %s-%s-%s' % (str(date.year), str(date.month), str(date.day)))
    finally:
        lock.release()

def filter_data(data_array):
    'Remove Fund Unsuppor'
    from DB_unsupport import DB_unsupport
    db = DB_unsupport()
    unsupports = db.select_all()

    o1 = len(data_array)
    for unsupport in unsupports:
        for index,fund in enumerate(data_array):        
            if fund['基金代码'] == unsupport:
                print('移除基金 代码 : %s'%fund['基金代码'])
                del data_array[index]
    o2 = len(data_array)
    print('基金数量:原 %s 个, 剩余 %s 个, 已移除 %s 个基金'%(str(o1), str(o2), str(o1-o2),))
    
#================ Run =========================
def get_funds(data_array, date=None):
    '''
    Get Funds
    Param:
        data_array : 基金数据 , shape = (array, map))
        date : 设定日期
    '''

    if date == None:
        date = datetime.datetime.now()

    print('Getting Fund Details ...')
    funds(data_array)
    filter_data(data_array)
    #TODO : 加入历史记录
    add_history(data_array, date=date)
    print('Finished Getting Fund Detail !')
    return data_array
    
