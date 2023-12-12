import numpy as np
import sys, json
from decimal import ROUND_HALF_UP
from decimal import Decimal
import pandas as pd
from Ashare import get_price
import warnings
warnings.filterwarnings("ignore")

def siwu(num):
    return Decimal(str(num)).quantize(Decimal('0.01'), ROUND_HALF_UP)

def cal(code, start_price, current_bottom):
    if code.startswith('sh6') or code.startswith('sz0'):
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

def gen_max_min(code, indf):
    df = indf.copy()
    df['z_scores'] = (df['volume'] - df['volume'].mean()) / df['volume'].std()
    df['index'] = np.arange(df.shape[0])
    df['inc'] = np.zeros(df.shape[0])
    for index in range(df.shape[0]):
        if index > 0:
            df['inc'].iloc[index] = siwu((df['close'].iloc[index] - df['close'].iloc[index-1]) / df['close'].iloc[index-1] * 100)
    threshold = 2
    outliers = df[df['z_scores'] > threshold]
    if outliers.shape[0] == 0:
        return None, None, None
    outliers['index_diff'] = np.zeros(outliers.shape[0])
    for index in range(outliers.shape[0]):
        if index > 0:
            outliers['index_diff'].iloc[index] = outliers['index'].iloc[index] - outliers['index'].iloc[index-1]
    volume_start = 1000000
    for index in range(1, outliers.shape[0]+1):
        if outliers['index_diff'].iloc[0-index] > 1 and outliers['inc'].iloc[0-index] > 0:
            volume_start = outliers['index'].iloc[0-index]
            if df['index'].iloc[-1] - volume_start < 3:
                print('%s volume big too close'%code)
                continue
            break
    if volume_start == 1000000:
        volume_start = outliers['index'].iloc[0]
    new_volume_start = volume_start - 3
    if new_volume_start < 0:
        new_volume_start = 0

    base_df = df.iloc[new_volume_start:]
    #if code == 'sz002709':
    #    print(code)
    #    print(df)
    #    print(outliers)
    #    print(volume_start)
    #    print(base_df)
    return base_df.iloc[3].name.strftime('%Y-%m-%d'), base_df['high'].max(), base_df['low'].min()


def main():
    final_lis = []
    with open(sys.argv[1]) as fi, open('mid_res','w') as fo:
        for line in fi:
            line = line.strip()
            code = line[1:]
            #if int(code) <= 301507:
            #    continue
            if code[0] in ['0','3']:
                code = 'sz' + code
            elif code[0] == '6':
                code = 'sh' + code
            else:
                continue
            current_df = get_price(code, frequency='1d', count=360)
            if current_df.shape[0] == 0:
                continue
            ymd, max_price, min_price = gen_max_min(code, current_df)
            if not ymd:
                continue
            res_dic = cal(code,max_price,min_price)
            if res_dic and res_dic['cum_amount'] >= 100:
                #max_price = current_df['high'].max()
                current_close_price = current_df['close'].iloc[-1]
                res_dic['cal_ymd'] = ymd
                #res_dic['max_120d'] = max_price
                #res_dic['min_120d'] = min_price
                res_dic['current_price'] = current_close_price
                res_dic['diff'] = siwu((current_close_price - float(res_dic['cost_line'])) / float(res_dic['cost_line']) * 100)
                print(list(res_dic.values()))
                #fo.write('%s\t%f\t%f\t%d\t%f\t%d\t%f\t%d\t%f\t%f\t%s\t%f\t%f\n'%(list(res_dic.values())))
                #fo.flush()
                #res_dic['max_diff'] = siwu((res_dic['max_120d'] - res_dic['start']) / res_dic['start'] * 100)
                final_lis.append(res_dic)
    final_df = pd.DataFrame(final_lis)
    final_df = final_df.sort_values(by="diff", ascending=False)
    print(final_df)
    final_df.to_csv('final_res_1.csv')
    print(final_df['cum_money'].sum())

if __name__ == "__main__":
    main()
