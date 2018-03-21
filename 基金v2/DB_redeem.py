import threading

import pymysql
from chromedriver import web_driver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
from browser_pool import browser_pool

#============ Configer ==============================
bar_lengh = 60

UseFundDB = True
isMultipleThread = True
ThreadAmount = 9999 # 总线程数
#============ Debug ================================
use_bar = True # 加载进度条
#============== DB ==================================
class DB_redeem:
    '''基金赎回信息类'''
##    table_name = 'test'
    table_name = 'redeem'
    
    connection = None
    
    def __init__(self):
        self.connection = pymysql.connect(host = 'localhost',
                             user = 'root',
                             password = 'root',
                             db = 'fund')

    def insert_redeem(self, code, redeem):
        with self.connection.cursor() as cursor:
            sql = """ INSERT INTO `"""+self.table_name+"""` (`code`, `fee`) VALUES ('"""+code+"""', """+str(redeem)+""")"""

            cursor.execute(sql)
            self.connection.commit()

    def get_redeem_by_code(self, code = 0):
        with self.connection.cursor() as cursor:
            sql = """SELECT fee FROM """+self.table_name+""" WHERE `code` = '"""+code+"""'"""

            cursor.execute(sql)
            result = cursor.fetchone()
            if result != None:
                try:
                    result = float(result[0])
                except ValueError:
                    result = None
        return result

    def close(self):
        self.connection.close()
#================ Add Redeem Fee ========================
def addRedeemFee(data_array):
    byTTFund(data_array)


def byTongHuaSun(data_array):
    print('Adding Redeem Fee ... ')
    url = "http://tools.fund.10jqka.com.cn/calculator/redeem.html"
    browser = web_driver()
    fundDB = DB_redeem()
    print('Getting page ==> ', url)
    browser.get(url)
    print('Adding Redemption Rates:')
    # Map for Delete_Cache
    map_del_s = []
    # Scope
    for map_ in tqdm(data_array, ncols=bar_lengh):
        ##    for map_ in data_array:
        rate = None  # 赎回费率初始化
        rate = fundDB.get_redeem_by_code(map_['基金代码'])
        if rate == None:
            elem = browser.find_element_by_id('hqjij')
            elem.clear()
            elem.send_keys(map_['基金代码'])
            clock = time.clock()
            while True:
                if time.clock() - clock > 5: break
                soup = BeautifulSoup(browser.page_source, "html.parser")
                if soup.find(id='hqjij').previous_sibling[
                    'style'] != 'left: 0px; top: 21px; width: 214px; z-index: 9999; display: none;':
                    break

            promoteDis_1 = BeautifulSoup(browser.page_source, "html.parser").find(id='promoteDis')
            clock = time.clock()
            while True:
                if time.clock() - clock > 5: break
                if promoteDis_1 != None:
                    if BeautifulSoup(browser.page_source, "html.parser").find(id='promoteDis') != None \
                            and BeautifulSoup(browser.page_source, "html.parser").find(
                        id='promoteDis').get_text() != promoteDis_1.get_text():
                        break
                elif BeautifulSoup(browser.page_source, "html.parser").find(id='promoteDis') != None:
                    break
                elem.send_keys(Keys.RETURN)

            soup = BeautifulSoup(browser.page_source, "html.parser")
            trs = soup.find(id='promoteDis').table.tbody.find_all('tr')
            trs = trs[1:]

            for tr in trs:
                try:
                    rate_temp = float(tr.find_all('td')[1].get_text().replace('%', '').replace(' ', ''))
                    if rate == None or rate < rate_temp:
                        rate = rate_temp
                except ValueError:
                    pass

            if rate != None:
                fundDB.insert_redeem(map_['基金代码'], rate)

        if rate != None:
            map_['赎回费率'] = rate
        else:
            map_del_s.append(map_)
    print("Removing Data which doesn't have [赎回费率] ...")
    for map_del_ in tqdm(map_del_s, ncols=bar_lengh):
        data_array.remove(map_del_)
    fundDB.close()
    browser.quit()
    print('Finished Adding Redeem Fee !')

def byTTFund(data_array):
    print('Adding Redeem Fee ... ')
    url = "http://fund.eastmoney.com/f10/jjfl_{}.html"
    fundDB = DB_redeem()
    print('Adding Redemption Rates:')
    # Map for Delete_Cache
    map_del_s = []

    # 初始化 从网页获取 赎回费率 计数
    import get_Redeem_from_Page_Amount
    get_Redeem_from_Page_Amount.amount = 0
    # Scope
    if isMultipleThread:
        multiple_thread_TTFund(data_array, fundDB, map_del_s, url)
    else:
        single_thread_TTFund(data_array, fundDB, map_del_s, url)

    print("Removing Data which doesn't have [赎回费率] ...")
    for map_del_ in tqdm(map_del_s, ncols=bar_lengh):
        data_array.remove(map_del_)
    fundDB.close()

    print('Finished Adding Redeem Fee !')

def single_thread_TTFund(data_array, fundDB, map_del_s, url):
    '''
    单线程打开【天天基金网】获取【赎回费率】
    :param data_array:
    :param fundDB:
    :param map_del_s:
    :param url:
    :return:
    '''
    for map_ in tqdm(data_array, ncols=bar_lengh):
        TTFund_Thread(fundDB, map_, map_del_s, url,)

def multiple_thread_TTFund(data_array, fundDB, map_del_s, url):
    '''
    多线程打开【天天基金网】获取【赎回费率】
    :param data_array:
    :param fundDB:
    :param map_del_s:
    :param url:
    :return:
    '''
    lock = threading.Lock()
    thread_amount = 0
    threads = []
    #TODO : get redeem start
    if use_bar:
        pbar = tqdm(total=len(data_array), ncols=bar_lengh)
    else:
        pbar = None
    # for map_ in tqdm(data_array, ncols=bar_lengh):
    for map_ in data_array:
        thread_amount += 1
        thread = threading.Thread(target=TTFund_Thread, args=(fundDB, map_, map_del_s, url, lock, pbar))
        thread.start()
        threads.append(thread)
        if thread_amount >= ThreadAmount:
            thread_amount = 0
            for thread in threads:
                thread.join()
            threads = []
        for thread in threads:
            thread.join()
    # 不能整除ThreadAmount(总线程数)个时
    if use_bar:
        pbar.close()


def TTFund_Thread(fundDB, map_, map_del_s, url, lock=None, pbar = None):
    ##    for map_ in data_array:
    rate = None  # 赎回费率初始化

    def get_redeem_by_code(fundDB, map_, rate):
        if UseFundDB:
            rate = fundDB.get_redeem_by_code(map_['基金代码'])
            return rate
        else:
            return None

    if lock == None:
        rate = get_redeem_by_code(fundDB, map_, rate)
    else:
        lock.acquire()
        try:
            rate = get_redeem_by_code(fundDB, map_, rate)
        finally:
            lock.release()

    if rate == None:
        # 从网页获取 赎回费率 计数+1
        import get_Redeem_from_Page_Amount
        get_Redeem_from_Page_Amount.amount += 1

        browser = browser_pool.acquire()

        browser.get(url.format(map_['基金代码']))
        # Abandon
        # elem = browser.find_element_by_xpath("//div[@id='bodydiv']/div[8]/div[3]/div[2]/div[3]/div/div[7]/div/table/tbody")
        soup = BeautifulSoup(browser.page_source, "html.parser")
        import re
        elem = soup.find_all(name='th', attrs={'class': 'last fl'}, text=re.compile("赎回费率"))
        if len(elem) < 1:
            print('未找到【赎回费率】，请修改BUG，基金代码：{}'.format(map_['基金代码']))
            c = input('输入【c】继续程序,其他按键退出...')
            if c != 'c':
                exit(0)
        else:
            elem = elem[0]

        parents = elem.parents
        for parent in parents:
            if parent.name == 'table':
                elem = parent
        elem = elem.tbody
        trs = elem.find_all('tr')
        for tr in trs:
            rate_temp = tr.find_all("td")[2].text.replace(' ', '').replace('%', '')
            try:
                rate_temp = float(rate_temp)
            except ValueError:
                rate_temp = None
                print('基金代码:', map_['基金代码'], '未找到【赎回费率】')
            if rate_temp != None and rate == None:
                rate = rate_temp
            elif rate_temp != None and rate_temp > rate:
                rate = rate_temp
        browser.release()

        def insert_redeem(map_, rate):
            if UseFundDB:
                fundDB.insert_redeem(map_['基金代码'], rate)
            else:
                print("【伪】插入数据库{}-{}".format(map_['基金代码'], rate))


        if lock == None:
            if rate != None:
                insert_redeem(map_, rate)
            else:
                map_del_s.append(map_)
        else:
            lock.acquire()
            try:
                if rate != None:
                    insert_redeem(map_, rate)
                else:
                    map_del_s.append(map_)
            finally:
                lock.release()
    map_['赎回费率'] = rate
    if use_bar:
        pbar.update(1)

if __name__ == '__main__':
    byTTFund([{'基金代码' : '002690'}])