import urllib3 as ul3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
import sys
import copy
import time

from redeem2DB import FundDB

'''
    股票基金评分排名系统
    url : http://fund.eastmoney.com/data/fundranking.html
'''
#============= Configer =======================
bar_lengh = 60

fund_types = ['股票型', '混合型', '债券型', '指数型']
#============ Global Data =====================
data_array = [] # 基金数据 , shape = (array, map)
data_date = {'month' : 0, 'day' : 0} # 基金数据获取日期
fundDB = FundDB() #赎回连接对象
#========= Rubbish Data =========================
remove_data = [] #被删除的基金
#============ Tools ===========================
def web_driver():
    '''浏览器驱动'''
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    # 无头浏览
    browser = webdriver.Chrome(chrome_options=chrome_options)
    # 有头浏览
##    browser = webdriver.Chrome()
    return browser
def init_Rank_Sort(map_):
    '''Add&Init key-[rank] to Map'''
    map_['rank'] = 0
def combine_rank(orig_, rank):
    '''combine rank from [rank] to [orig_]'''
    for index,rank_ in enumerate(rank):
        for orig__ in orig_:
            if orig__['基金代码'] == rank_['基金代码']:
                orig__['rank'] += index
def wait_action(browser, name=None):
    if name == None: name = ''
    else: name = '['+str(name)+']'
    print(name+'Waiting for Reflesh ...')
    while(BeautifulSoup(browser.page_source, "html.parser").get_text().find('长时间不更新') != -1):
        ''' Waiting for Reflesh '''
        pass
    print('Reflesh Done.')
#============ Get Fund Detail =======================
url = "http://fund.eastmoney.com/data/fundranking.html"
browser = web_driver()
print('Getting page ==> ', url)
browser.get(url)

for fund_type in fund_types:
    print('Getting Fund Data (', fund_type, ') ...')
    lis = browser.find_elements_by_tag_name('li')
    for li in lis:
        soup = BeautifulSoup(li.text, "html.parser")
        if soup.get_text().find(fund_type)>-1:
            ActionChains(browser).click(li).perform()
            break
    wait_action(browser)

    soup = BeautifulSoup(browser.page_source, "html.parser")
    trs = soup.find(id='dbtable').tbody.findAll('tr')
    if len(trs) <= 50:
        ActionChains(browser).click(browser.find_element_by_id('showall')).perform()
        wait_action(browser, '点击<showall>')        
        soup = BeautifulSoup(browser.page_source, "html.parser")
        trs = soup.find(id='dbtable').tbody.findAll('tr')

    # Data Date
    try:
        tr = trs[0]
        tds = tr.findAll('td')
        date = tds[4].get_text().replace(' ', '').split('-')
        data_date['month'] = int(date[0])
        data_date['day'] = int(date[1])
    except ValueError:
        data_date['month'] = 0
        data_date['day'] = 0
    if data_date['month'] == 0 or data_date['day'] == 0:
        print('ERROR : 未能获取数据时间！')
    else:
        print('数据时间 (' + fund_type + ') -->', data_date['month'], '月', data_date['day'], '日')

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

browser.quit()

#============== 加入赎回手续费 ===================================
url = "http://tools.fund.10jqka.com.cn/calculator/redeem.html"
browser = web_driver()
print('Getting page ==> ', url)
browser.get(url)
print('Adding Redemption Rates:')
#Scope
for map_ in tqdm(data_array, ncols=bar_lengh):
##for map_ in data_array:
    rate = None #赎回费率初始化
    rate = fundDB.get_redeem_by_code(map_['基金代码'])
    if rate == None:
        elem = browser.find_element_by_id('hqjij')
        elem.clear()
        elem.send_keys(map_['基金代码'])
        clock = time.clock()
        while True:
            if time.clock()-clock > 5 : break
            soup = BeautifulSoup(browser.page_source, "html.parser")
            if soup.find(id='hqjij').previous_sibling['style'] != 'left: 0px; top: 21px; width: 214px; z-index: 9999; display: none;':
                break

        promoteDis_1 = BeautifulSoup(browser.page_source, "html.parser").find(id='promoteDis')
        clock = time.clock()
        while True:
            if time.clock()-clock > 5 : break
            if promoteDis_1 != None:
                if BeautifulSoup(browser.page_source, "html.parser").find(id='promoteDis') != None \
                and BeautifulSoup(browser.page_source, "html.parser").find(id='promoteDis').get_text() != promoteDis_1.get_text():
                    break
            elif BeautifulSoup(browser.page_source, "html.parser").find(id='promoteDis') != None:
                break
            elem.send_keys(Keys.RETURN)

        soup = BeautifulSoup(browser.page_source, "html.parser")
        trs = soup.find(id='promoteDis').table.tbody.find_all('tr')
        trs = trs[1:]

        for tr in trs:
            try:
                rate_temp = float(tr.find_all('td')[1].get_text().replace('%','').replace(' ',''))
                if rate == None or rate < rate_temp:
                    rate = rate_temp
            except ValueError:
                pass
            
        if rate != None:
            fundDB.insert_redeem(map_['基金代码'], rate)

    if rate != None:
        map_['赎回费率'] = rate
    else:
        remove_data.append(copy.deepcopy(map_))
        del map_
    
fundDB.close()
browser.quit()

#============== Rank ============================================
for map_ in data_array:
    init_Rank_Sort(map_)

日增长率_sorted = sorted(data_array, key=lambda x : x['日增长率']-x['手续费']-x['赎回费率'], reverse=True)
近1周_sorted = sorted(data_array, key=lambda x : x['近1周']-x['手续费']-x['赎回费率'], reverse=True)
近1月_sorted = sorted(data_array, key=lambda x : x['近1月']-x['手续费']-x['赎回费率'], reverse=True)
近3月_sorted = sorted(data_array, key=lambda x : x['近3月']-x['手续费']-x['赎回费率'], reverse=True)
近6月_sorted = sorted(data_array, key=lambda x : x['近6月']-x['手续费']-x['赎回费率'], reverse=True)
近1年_sorted = sorted(data_array, key=lambda x : x['近1年']-x['手续费']-x['赎回费率'], reverse=True)
近2年_sorted = sorted(data_array, key=lambda x : x['近2年']-x['手续费']-x['赎回费率'], reverse=True)

combine_rank(data_array, 日增长率_sorted)
combine_rank(data_array, 近1周_sorted)
combine_rank(data_array, 近1月_sorted)
combine_rank(data_array, 近3月_sorted)
combine_rank(data_array, 近6月_sorted)
combine_rank(data_array, 近1年_sorted)
combine_rank(data_array, 近2年_sorted)

total_rank = sorted(data_array, key=lambda x : x['rank'])
print('=========================== Rank ======================================')
for index,item in enumerate(total_rank):
    print(index, item['基金代码'], item['基金简称'], item['rank'])

#=========== GUI for Search ======================
import tkinter as tk

root = tk.Tk()
root.title('股票基金评分排名')

def entry_Return(event):
    button_action()
entry = tk.Entry(root)
entry.bind('<Return>', entry_Return)
entry.grid(row=0, column=2)

def button_action():
    try:
        if int(entry.get()) >= len(total_rank):
            label['text'] = 'Sorry!No found.'
        else:
            detail = total_rank[int(entry.get())]
            label['text'] = 'rank:' + entry.get() + '\n'\
                            + '基金代码:' + str(detail['基金代码']) + '\n'\
                            + '基金简称:' + str(detail['基金简称']) + '\n'\
                            + '日增长率:' + str(detail['日增长率']) + '%\n'\
                            + '近1周:' + str(detail['近1周']) + '%\n'\
                            + '近1月:' + str(detail['近1月']) + '%\n'\
                            + '近3月:' + str(detail['近3月']) + '%\n'\
                            + '近6月:' + str(detail['近6月']) + '%\n'\
                            + '近1年:' + str(detail['近1年']) + '%\n'\
                            + '近2年:' + str(detail['近2年']) + '%\n'\
                            + '手续费:' + str(detail['手续费']) + '%\n'\
                            + '赎回费率:' + str(detail['赎回费率']) + '%'
                                           
    except ValueError:
        label['text'] = "Please input correct 'Number' !"
button = tk.Button(root, text='Check', command=button_action)
button.grid(row=0, column=3)

def button_code_action():
    code = ''
    try:
        int(entry.get())
        code = entry.get()
    except ValueError:
        code = 0
    detail = None
    rank_index = '---'
    for index,fund in enumerate(total_rank):
        if str(fund['基金代码']) == code:
            detail = fund
            rank_index = index
    if rank_index == '---':
        label['text'] = 'Sorry!No found.'
    else:
        label['text'] = 'rank:' + str(rank_index) + '\n'\
                        + '基金代码:' + str(detail['基金代码']) + '\n'\
                        + '基金简称:' + str(detail['基金简称']) + '\n'\
                        + '日增长率:' + str(detail['日增长率']) + '%\n'\
                        + '近1周:' + str(detail['近1周']) + '%\n'\
                        + '近1月:' + str(detail['近1月']) + '%\n'\
                        + '近3月:' + str(detail['近3月']) + '%\n'\
                        + '近6月:' + str(detail['近6月']) + '%\n'\
                        + '近1年:' + str(detail['近1年']) + '%\n'\
                        + '近2年:' + str(detail['近2年']) + '%\n'\
                        + '手续费:' + str(detail['手续费']) + '%\n'\
                        + '赎回费率:' + str(detail['赎回费率']) + '%'
        
button_code = tk.Button(root, text='Code', command=button_code_action)
button_code.grid(row=0, column=4)

label = tk.Label(root)
label.grid(row=1, column=2, columnspan=3)

root.mainloop()
