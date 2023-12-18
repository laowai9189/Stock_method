import pandas as pd
import requests, json
from concurrent.futures import ThreadPoolExecutor

df = pd.read_csv('final_res_1218.csv', index_col='index')
#df = df[(df['diff'] >= -10.0) & (df['diff'] <= 0.0)]
df = df[(df['diff'] >= 0.0) & (df['diff'] <= 10.0)]
print(df)


def get_amo(row):
    code = row[1]['code']
    api_url = "http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=%s,day,,,2,qfq"%code
    while True:
        try:
            st = json.loads(requests.get(api_url).content)
            break
        except:
            continue
    return st['data'][code]['qt'][code][57]

with ThreadPoolExecutor(max_workers=16) as executor:
    result = list(executor.map(get_amo, df.iterrows()))
df['amo'] = result
print(df)
df.to_csv('dai_amo_1218_positive.csv')