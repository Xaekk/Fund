from browser_pool import browser_pool
from fund_detail import get_funds
from DB_dailyrate import add_dailyrate
from DB_redeem import addRedeemFee
from fund_rank import fundRank
from fund_gui import fund_gui
import webbrowser as WB
import datetime

def run():
    data_array = []

    day, month, year = getDate()

    #Get data from Page
    get_funds(data_array, date=datetime.date(year, month, day))
##    data_array = data_array[:2]
    
    #add redeem fee
    addRedeemFee(data_array)
    
    #add latest 30 days rate
##    add_dailyrate(data_array)
    
    #rank
    data_array = fundRank(data_array)

    return data_array


def getDate():
    while (1):
        data_temp = datetime.datetime.now()
        year = input('设定-年 : ')
        month = input('设定-月 : ')
        day = input('设定-日 : ')

        try:
            year = int(year)
        except ValueError:
            year = data_temp.year
        try:
            month = int(month)
        except ValueError:
            month = data_temp.month
        try:
            day = int(day)
        except ValueError:
            day = data_temp.day

        correct = input("设定日期为 : {}年{}月{}日, 键入【r】重置".format(year, month, day))
        if correct != 'r':
            break
    return day, month, year


if __name__ == '__main__':
    data_array = run()
    browser_pool.close()
    WB.open('http://fund.eastmoney.com/data/fundranking.html#tall;pn10000')
    fund_gui(data_array)
