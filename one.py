import numpy as np
import sys
from decimal import ROUND_HALF_UP
from decimal import Decimal

def siwu(num):
    return Decimal(str(num)).quantize(Decimal('0.01'), ROUND_HALF_UP)

start_price = float(sys.argv[1])
current_bottom = float(sys.argv[2])
money_lis = np.array([1,2,4,8,16,32,64]) * 1100
cost_line = [siwu(start_price * (1 - 0.08 * (i + 1))) for i in range(7)]
print(cost_line)
#share_lis = [siwu(np.sum(money_lis[:i+1]) / cost_line[i]) // 100 * 100 for i in range(7)]
#share_lis = [siwu(np.sum(money_lis[:i+1]) / cost_line[i]) for i in range(7)]
share_lis = [np.sum(money_lis[:i+1]) / cost_line[i] for i in range(7)]
print(share_lis)
for i in range(7):
    if i == 0:
        true_share = share_lis[0]
    else:
        true_share = share_lis[i] - share_lis[i-1]
    buy_price = siwu(money_lis[i] / true_share)
    print('第%d次'%(i+1))
    print('购买价格：',buy_price)
    print('购买金额：',money_lis[i])
    print('购买数量：',siwu(true_share))
    print('累计金额：',np.sum(money_lis[:i+1]))
    print('累计数量：',siwu(share_lis[i]))
    print('购买后成本线：',cost_line[i])
    print()
