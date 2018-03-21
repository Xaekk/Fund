import os

import fund_detail
import DB_redeem
from browser_pool import browser_pool

def run():
    data_array = []
    print('Getting Fund Details ...')
    fund_detail.funds(data_array)
    fund_detail.filter_data(data_array)
    print('Finished Getting Fund Detail !')
    while True:
        DB_redeem.addRedeemFee(data_array)

        import get_Redeem_from_Page_Amount
        if get_Redeem_from_Page_Amount.amount <1:
            break

    browser_pool.close()
    print('Done!')

if __name__ == '__main__':
    run()