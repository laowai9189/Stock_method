import numpy as np
import sys
from decimal import ROUND_HALF_UP
from decimal import Decimal
import pandas as pd

def siwu(num):
    return Decimal(str(num)).quantize(Decimal('0.01'), ROUND_HALF_UP)

def cal(code, start_price, current_bottom):
    if code.startswith('a_6') or code.startswith('a_0'):
        dec_rate = 0.08
    else:
        dec_rate = 0.1
    money_lis = np.array([1,2,4,8,16,32,64]) * 1100
    cost_line = [siwu(start_price * (1 - dec_rate * (i + 1))) for i in range(7)]
    share_lis = [np.sum(money_lis[:i+1]) / cost_line[i] for i in range(7)]
    res_dic = dict()
    res_lis = []
    for i in range(7):
        if i == 0:
            true_share = share_lis[0]
        else:
            true_share = share_lis[i] - share_lis[i-1]
        buy_price = siwu(money_lis[i] / true_share)
        res_dic = {'code':code, 'start':start_price, 'bottom':current_bottom, 'time':i+1, 'price':buy_price, 'money':money_lis[i], 'amount':siwu(true_share), 'cum_money':np.sum(money_lis[:i+1]), 'cum_amount':siwu(share_lis[i]), 'cost_line':cost_line[i]}
        res_lis.append(res_dic)
        if buy_price < current_bottom:
            if len(res_lis) >= 2:
                return res_lis[-2]
            else:
                return None

def main():
    df = pd.read_csv('ttt.csv',index_col=None)
    final_lis = []
    for index, row in df.iterrows():
        res_dic = cal(row['code'],row['start'],row['bottom'])
        if res_dic:
            final_lis.append(res_dic)
    final_df = pd.DataFrame(final_lis)
    print(final_df)

if __name__ == "__main__":
    main()
