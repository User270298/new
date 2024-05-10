from pybit.unified_trading import WebSocket
from time import sleep
import json
from datetime import datetime
import pandas as pd
import csv
df = pd.DataFrame()
ws = WebSocket(
    testnet=True,
    channel_type="linear",
)
print('Start')
with open("classmates.csv", mode="a", encoding='utf-8') as w_file:
    file_writer = csv.writer(w_file, delimiter=",", lineterminator="\r")
    file_writer.writerow(["timestamp", "open", "high", "low", "close", "volume"])
def handle_message(message):
    try:
        info=message['data'][0]
        opened=info['open']
        close=info['close']
        high=info['high']
        low=info['low']
        volume=info['volume']
        timeframe=str(datetime.fromtimestamp(int(message['ts'])/1000))
        timeframe=timeframe[:19]
        # print(timeframe)
        # print(timeframe[14:16])
        # print(int(timeframe[14:16]),':',str(timeframe[17:19]))
        if int(timeframe[14:16])%15==0 and str(timeframe[17:19])=='00': #int(timeframe[14:16])%5==0 and
            # print('Yes')
            with open("classmates.csv", mode="a", encoding='utf-8') as w_file:
                file_writer = csv.writer(w_file, delimiter=",", lineterminator="\r")
                file_writer.writerow([timeframe, opened, high, low, close, volume])
    except Exception as e:
        print(e)

ws.kline_stream(
        interval=15,
        symbol="BTCUSDT",
        callback=handle_message)
while True:
    sleep(1)

# #{'topic': 'kline.1.ETHUSDT', 'data': [{'start': 1714474440000, 'end': 1714474499999, 'interval': '1', 'open': '303
# 8.14', 'close': '3037.13', 'high': '3038.14', 'low': '3036.35', 'volume': '220.56', 'turnover': '669809.5108', 'confirm': False, 'timestamp': 1714474460602}], 'ts': 1714474460602, 'type': 'snapshot'}


