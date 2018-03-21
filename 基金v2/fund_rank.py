from tqdm import tqdm
#============= Configer =========================================
bar_lengh = 60
#============== Tools ===========================================
def init_Rank_Sort(map_):
    '''Add&Init key-[rank] to Map'''
    map_['rank'] = 0
def combine_rank(orig_, rank, times = 1):
    '''combine rank from [rank] to [orig_]'''
    for _ in range(times):
        for index,rank_ in enumerate(rank):
            for orig__ in orig_:
                if orig__['基金代码'] == rank_['基金代码']:
                    orig__['rank'] += index
#============== Rank ============================================
def fundRank(data_array):
    print('Ranking ... ')
    for map_ in data_array:
        init_Rank_Sort(map_)

    日增长率_sorted = sorted(data_array, key=lambda x : x['日增长率']-x['手续费']-x['赎回费率'], reverse=True)
    近1周_sorted = sorted(data_array, key=lambda x : x['近1周']-x['手续费']-x['赎回费率'], reverse=True)
    近1月_sorted = sorted(data_array, key=lambda x : x['近1月']-x['手续费']-x['赎回费率'], reverse=True)
    近3月_sorted = sorted(data_array, key=lambda x : x['近3月']-x['手续费']-x['赎回费率'], reverse=True)
    近6月_sorted = sorted(data_array, key=lambda x : x['近6月']-x['手续费']-x['赎回费率'], reverse=True)
    近1年_sorted = sorted(data_array, key=lambda x : x['近1年']-x['手续费']-x['赎回费率'], reverse=True)
    近2年_sorted = sorted(data_array, key=lambda x : x['近2年']-x['手续费']-x['赎回费率'], reverse=True)
    费率_sorted = sorted(data_array, key=lambda x : x['手续费'] + x['赎回费率'])

##    combine_rank(data_array, 日增长率_sorted)
    combine_rank(data_array, 近1周_sorted)
    combine_rank(data_array, 近1月_sorted)
    combine_rank(data_array, 近3月_sorted)
    combine_rank(data_array, 近6月_sorted)
    combine_rank(data_array, 近1年_sorted)
    combine_rank(data_array, 近2年_sorted)
    combine_rank(data_array, 费率_sorted, times=2)

    #Scope
    #TODO : 历史记录不考虑 费率
    #历史记录 排名
    print('历史记录排名...')
    for index in tqdm(range(len(data_array[0]['历史记录'])), ncols=bar_lengh):
        sort = sorted(data_array, key=lambda x : x['历史记录'][index], reverse=True)
        combine_rank(data_array, sort)
    #最近三天历史记录 排名
    print('最近三天历史记录排名...')
    for index in tqdm(range(len(data_array[0]['最近三天历史记录'])), ncols=bar_lengh):
        sort = sorted(data_array, key=lambda x : x['最近三天历史记录'][index])
        combine_rank(data_array, sort)

    data_array = sorted(data_array, key=lambda x : x['rank'])
    print('Finished Ranking !')
    return data_array
