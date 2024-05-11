import okx.Account as Account
import okx.Trade as trade
import pprint
import datetime
import requests

TOKEN = '6959314930:AAHnekjhCc2d_CHFLxE9hFWAZuIgQMD8wzY'
chat_id='947159905'

api_key='43f5df59-5e61-4d24-875e-f32c003e0430'
secret_key='5B1063B322635A27CF01BACE3772E0E0'
passphrase='Parkwood270298)'
flag = "1"  # live trading: 0, demo trading: 1
accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
tradeAPI = trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
result = tradeAPI.get_orders_history(
    instType="SWAP"
)
x=result['data']
res_pnl=0
win_rate=0
# pprint.pprint(x)
date_extreme=datetime.datetime.fromtimestamp(int(x[0]['fillTime'])/1000)
date_extreme=str(date_extreme)[:10]
count_plus=0
count_minus=0
#{'accFillSz': '10', 'algoClOrdId': '', 'algoId': '', 'attachAlgoClOrdId': '', 'attachAlgoOrds': [], 'avgPx': '60626.1', 'cTime': '1715366309473', 'cancelSource': '', 'cancelSourceReason': '', 'category': 'normal', 'ccy': '', 'clOrdId': '', 'fee': '-0.3031305', 'feeCcy': 'USDT', 'fillPx': '60626.1', 'fillSz': '10', 'fillTime': '1715366309474', 'instId': 'BTC-USDT-SWAP', 'instType': 'SWAP', 'isTpLimit': 'false', 'lever': '20.0', 'linkedAlgoOrd': {'algoId': ''}, 'ordId': '1438274135692328960', 'ordType': 'market', 'pnl': '18.916', 'posSide': 'short', 'px': '', 'pxType': '', 'pxUsd': '', 'pxVol': '', 'quickMgnType': '', 'rebate': '0', 'rebateCcy': 'USDT', 'reduceOnly': 'true', 'side': 'buy', 'slOrdPx': '', 'slTriggerPx': '', 'slTriggerPxType': '', 'source': '', 'state': 'filled', 'stpId': '', 'stpMode': 'cancel_maker', 'sz': '10', 'tag': '', 'tdMode': 'isolated', 'tgtCcy': '', 'tpOrdPx': '', 'tpTriggerPx': '', 'tpTriggerPxType': '', 'tradeId': '940364590', 'uTime': '1715366309475'}
for i in x:
    if i['pnl']!='0':
        date=datetime.datetime.fromtimestamp(int(i['fillTime'])/1000)
        date_end=str(date)[:10]
        if date_extreme==date_end:
            res_pnl+=float(i['pnl'])
            print(date)
            print(float(i['pnl']))
            if float(i['pnl'])>0:
                count_plus+=1
            if float(i['pnl'])<0:
                count_minus+=1
print(f'Дата {date_extreme}')
print(f'Суммарный pnl: {round(res_pnl, 2)} USDT')
print(f'Win rate: {round((count_plus / count_minus)*100, 0)} %')
message = (f'Дата {date_extreme}\n'
           f'Суммарный pnl: {round(res_pnl, 2)} USDT\n'
           f'Win rate {round((count_plus / count_minus)*100, 0)} %')
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
requests.get(url).json()