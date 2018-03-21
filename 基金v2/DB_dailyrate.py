import pymysql
import datetime
from chromedriver import web_driver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
#=============== Configer ================================
bar_lengh = 60
#================== DB ===================================
class DB_dailyrate:
    '''[dailyrate]数据库'''
    # Table Name
    table_name = 'dailyrate'

    connection = None

    def __init__(self):
        '''Initalize'''
        self.connection = pymysql.connect(host = 'localhost',
                             user = 'root',
                             password = 'root',
                             db = 'fund')

    def insert(self, code, rate, month, day, year=2018):
        '''Insert into [dailyrate]'''
        code = str(code)
        rate = str(rate)
        month = str(month)
        day = str(day)
        year = str(year)
        date = year + '-' + month + '-' + day
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO `%s` (`code`, `date`, `rate`) VALUES ('%s', '%s', '%s')"%(self.table_name, code, date,rate)
##            print(sql)
            cursor.execute(sql)
            self.connection.commit()

    def select(self, code, month, day, year=2018):
        '''Select from [dailyrate]'''
        code = str(code)
        month = str(month)
        day = str(day)
        year = str(year)
        date = year + '-' + month + '-' + day
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM `%s` WHERE `code` = '%s' AND `date` = '%s' "%(self.table_name, code, date)
##            print(sql)            
            cursor.execute(sql)
            result = cursor.fetchone()
        if result != None:
            try:
                rate = float(result[3])
            except ValueError:
                print("类型转换[float]错误-->",'值:',result[3])
                print('错误位置-->table:%s, id:%s'%(table_name,result[0]))
        else:
            rate = None
        return rate

    def close(self):
        self.connection.close()

def add_dailyrate_function(data_array):
    ''' Add Daily Rate Function '''
    db = DB_dailyrate()
    len_ = len(data_array)
    for index_fund,fund in enumerate(data_array):
        print('进度记录 : %s/%s'%(str(index_fund+1), str(len_)))
        date = datetime.datetime.now()
        fund['历史记录'] = []
        browser = web_driver()
        browser.get('http://fund.eastmoney.com/f10/jjjz_%s.html'%(fund['基金代码']))
        for _ in tqdm(range(30), ncols=bar_lengh):
            rate = db.select(code=fund['基金代码'], month=date.month, day=date.day , year=date.year)
            if rate == None:                
                ele_start = browser.find_element_by_id('lsjzSDate')
                ele_end = browser.find_element_by_id('lsjzEDate')
                ele_but = browser.find_element_by_css_selector('input.search')

                ele_start.clear()
                ele_end.clear()

                ele_start.send_keys('%s-%s-%s'%(str(date.year) if date.year>=10 else '0'+str(date.year),str(date.month) if date.month>=10 else '0'+str(date.month),str(date.day) if date.day>=10 else '0'+str(date.day)))
                ele_end.send_keys('%s-%s-%s'%(str(date.year) if date.year>=10 else '0'+str(date.year),str(date.month) if date.month>=10 else '0'+str(date.month),str(date.day) if date.day>=10 else '0'+str(date.day)))
                ActionChains(browser).click(ele_but).perform()

                # Waiting
                while True:
                    if BeautifulSoup(browser.page_source, "html.parser").find(id='jztable').find('div') != None:
                        break
                while True:
                    if BeautifulSoup(browser.page_source, "html.parser").find(id='jztable').find('div') == None:
                        break
                page = BeautifulSoup(browser.page_source, "html.parser")
                if page.find(id='jztable').table.find('tbody').tr == None:
                    date = date - datetime.timedelta(days=1)
                    continue
                try:
                    rate = float(page.find(id='jztable').table.find('tbody').tr.findAll('td')[3].text.replace(' ','').replace('%',''))
                except ValueError:
                    rate = 0

                db.insert(code=fund['基金代码'], rate=rate, month=date.month, day=date.day, year=date.year)
            date = date - datetime.timedelta(days=1)
            fund['历史记录'].append(rate)                
        browser.quit()
            
    db.close()

#================== Run ===================================
def add_dailyrate(data_array):

    print('Adding Daily Rate ... ')
    add_dailyrate_function(data_array)
    print('Finished Adding Daily Rate !')
