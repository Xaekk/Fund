from fund_detail import get_funds
from DB_dailyrate import add_dailyrate
from DB_redeem import addRedeemFee
from fund_rank import fundRank
from fund_gui import fund_gui
import webbrowser as WB
from browser_pool import browser_pool

def run():
    data_array = []
    
    #Get data from Page
    get_funds(data_array)
##    data_array = data_array[:2]
    
    #add redeem fee
    addRedeemFee(data_array)
    
    #add latest 30 days rate
##    add_dailyrate(data_array)
    
    #rank
    data_array = fundRank(data_array)

    return data_array

if __name__ == '__main__':
    data_array = run()
    browser_pool.close()
    WB.open('http://fund.eastmoney.com/data/fundranking.html#tall;pn10000')
    fund_gui(data_array)
