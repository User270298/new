import okx.Account as Account
import okx.Trade as trade
import pprint
import requests
import datetime
from time import sleep
import pandas as pd
import numpy as np

#telegram
TOKEN = '6959314930:AAHnekjhCc2d_CHFLxE9hFWAZuIgQMD8wzY'
chat_id='947159905'

# print(requests.get(url).json())
#-------------------------------------

# live trading: 0, demo trading: 1
#OKX demo trading
# api_key='43f5df59-5e61-4d24-875e-f32c003e0430'
# secret_key='5B1063B322635A27CF01BACE3772E0E0'
# passphrase='Parkwood270298)'
# flag = "1"

#OKX live trading
api_key='f8bcadcc-bed3-4fca-96e7-4f314f43136b'
secret_key='F56CF3942B876FDEDEF547C90B04F206'
passphrase='Parkwood270298)'
flag = "0"

accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
tradeAPI = trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
#-------------------------------------------------
count_long=0
count_short=0
ordId=0
risk=5
foulder=20

while True:
    try:
    # в 1 час 12 раз по 5 минут, 4 раза по 15 минут, 2 раза по 30 минут
    # Нужно каждые 61 бар делать статистику
        for i in ["BTC-USDT-SWAP.csv", 'ETH-USDT-SWAP.csv', 'SOL-USDT-SWAP.csv']:
            coin = i
            df = pd.read_csv(i)
            pd.options.display.max_rows = 2000
            pd.set_option('display.max_rows', None)
            # df = df[:94]
            if len(df)>=1001:
                df = df.iloc[1:, :]
            # print(len(df))
            if len(df)>=41:
                result = accountAPI.get_positions()
                list_coins = []
                if len(result['data']) != 0:
                    for i in range(len(result['data'])):
                        res = result['data'][i]['instId']
                        list_coins.append(res)
                def isSwing(candle, window):
                    if candle - window < 0 or candle + window >= len(df):
                        return 0
                    # print(candle, window)
                    swingHigh = 1
                    swingLow = 2
                    for i in range(candle - window, candle + window + 1):
                        if df.iloc[candle].low > df.iloc[i].low:
                            swingLow = 0
                        if df.iloc[candle].high < df.iloc[i].high:
                            swingHigh = 0
                    if (swingHigh and swingLow):
                        return 3
                    elif swingHigh:
                        return swingHigh
                    elif swingLow:
                        return swingLow
                    else:
                        return 0
                window = 10
                df['isSwing'] = df.apply(lambda x: isSwing(x.name, window), axis=1)
                def pointpos(x):
                    if x['isSwing'] == 2:
                        return x['low']
                    elif x['isSwing'] == 1:
                        return x['high']
                    else:
                        return np.nan
                df['pointpos'] = df.apply(lambda row: pointpos(row), axis=1)
                def detect_structure(candle, backcandles, window):
                    localdf = df.iloc[
                              candle - backcandles - window:candle - window]  # window must be greater than pivot window to avoid look ahead bias
                    highs = localdf[localdf['isSwing'] == 1].high.tail(2).values
                    lows = localdf[localdf['isSwing'] == 2].low.tail(2).values
                    levelbreak = 0
                    zone_width = 0.001
                    if len(highs) == 2:  # long
                        resistance_condition = True
                        mean_high = highs.mean()
                        if resistance_condition and (df.loc[candle].close - mean_high) > zone_width * 2:
                            levelbreak = 1
                    if len(lows) == 2:  # short
                        support_condition = True
                        mean_low = lows.mean()
                        if support_condition and (mean_low - df.loc[candle].close) > zone_width * 2:
                            levelbreak = 2
                    return levelbreak
                df['pattern_detected'] = df.apply(lambda row: detect_structure(row.name, backcandles=60, window=9), axis=1)
                # print(df.tail(2))
                print(df["pattern_detected"].iloc[-1])
                # print(df['close'].iloc[-1])
                rslt_df_high = df[df['isSwing'] == 1]
                rslt_df_low = (df[df['isSwing'] == 2])
                high = rslt_df_high['pointpos'].iloc[-1]
                low = rslt_df_low['pointpos'].iloc[-1]
                close = df['close'].iloc[-1]
                coin=coin[:-4]

                if coin=='BTC-USDT-SWAP':
                    deliver=1000
                elif coin=='ETH-USDT-SWAP':
                    deliver=100
                elif coin=='SOL-USDT-SWAP':
                    deliver=10
                # "BTC-USDT-SWAP.csv", 'ETH-USDT-SWAP.csv', 'SOL-USDT-SWAP.csv'
                print(f'Coin: {coin}')
                # print(type(coin))
                # print(list_coins)
                if df["pattern_detected"].iloc[-1]==1 and (coin not in list_coins):
                    #Long
                    stop=low*0.9996
                    take = ((close-stop)*2.5)+close
                    percent_sz = ((risk / (foulder * ((close - stop) / stop))) * deliver) / close
                    print('------------LONG-------------')
                    print(f'Take {take}')
                    print(f'Coin {close}')
                    print(f'Stop {stop}')
                    result = tradeAPI.place_order(
                        instId=coin,
                        tdMode="isolated",
                        side="buy",
                        posSide="long",
                        ordType="market",
                        sz=round(percent_sz, 1),
                        tpTriggerPx=take,  # take profit trigger price
                        tpOrdPx="-1",  # taker profit order price。When it is set to -1，the order will be placed as an market order
                        tpTriggerPxType="last",
                        slTriggerPx=stop,      # take profit trigger price
                        slOrdPx="-1",           # taker profit order price。When it is set to -1，the order will be placed as an market order
                        slTriggerPxType="last"
                    )

                    message = (f'------LONG------- \n'
                               f'coin: {coin}\n'
                               f'Take profit {take}\n'
                               f'Coin {close}\n'
                               f'Stop loss {stop}')
                    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
                    requests.get(url).json()

                    # take = low * 0.995
                    # stop = (close - take) / 2 + close
                    # print('--------SHORT-----------')
                    # print(f'Take {take}')
                    # print(f'Coin {close}')
                    # print(f'Stop {stop}')
                    # result = tradeAPI.place_order(
                    #     instId=coin,
                    #     tdMode="isolated",
                    #     side="sell",
                    #     posSide="short",
                    #     ordType="market",
                    #     sz="10",
                    #     tpTriggerPx=take,
                    #     tpOrdPx="-1",
                    #     tpTriggerPxType="last",
                    #     slTriggerPx=stop,
                    #     slOrdPx="-1",
                    #     slTriggerPxType="last"
                    # )

                    # message = (f'------SHORT------- \n'
                    #            f'Coin: {coin}\n'
                    #           f'Take profit {take}\n'
                    #           f'Coin {close}\n'
                    #           f'Stop loss {stop}')
                    # url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
                    # requests.get(url).json()
                    # print(result)
                elif df["pattern_detected"].iloc[-1]==2 and (coin not in list_coins):
                    #Short
                    stop = high * 1.0004
                    take = close-((stop - close) * 2.5)
                    percent_sz = ((risk / (foulder * ((stop - close) / close))) * deliver) / close
                    print('------------SHORT-------------')
                    print(f'Stop {stop}')
                    print(f'Coin {close}')
                    print(f'Take {take}')
                    result = tradeAPI.place_order(
                        instId=coin,
                        tdMode="isolated",
                        side="sell",
                        posSide="short",
                        ordType="market",
                        sz=round(percent_sz, 1),
                        tpTriggerPx=take,  # take profit trigger price
                        tpOrdPx="-1",  # taker profit order price。When it is set to -1，the order will be placed as an market order
                        tpTriggerPxType="last",
                        slTriggerPx=stop,      # take profit trigger price
                        slOrdPx="-1",           # taker profit order price。When it is set to -1，the order will be placed as an market order
                        slTriggerPxType="last"
                    )
                    message = (f'------SHORT------- \n'
                               f'Coin: {coin}\n'
                              f'Take profit {take}\n'
                              f'Coin {close}\n'
                              f'Stop loss {stop}')
                    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
                    requests.get(url).json()
                    #

                    # take=high * 1.005
                    # stop=close-(take-close)/2
                    # print('------------LONG-------------')
                    # print(f'Take {take}')
                    # print(f'Coin {close}')
                    # print(f'Stop {stop}')
                    # result = tradeAPI.place_order(
                    #     instId=coin,
                    #     tdMode="isolated",
                    #     side="buy",
                    #     posSide="long",
                    #     ordType="market",
                    #     sz="10",
                    #     tpTriggerPx=take,
                    #     tpOrdPx="-1",
                    #     tpTriggerPxType="last",
                    #     slTriggerPx=stop,
                    #     slOrdPx="-1",
                    #     slTriggerPxType="last"
                    # )

                    # message = (f'------LONG------- \n'
                    #            f'Coin: {coin}\n'
                    #            f'Take profit {take}\n'
                    #            f'Coin {close}\n'
                    #            f'Stop loss {stop}')
                    # url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
                    # requests.get(url).json()
        sleep(60)
    except Exception as e:
        raise Exception(f'Invalid {е}')
        message = (f'{e}')
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
        requests.get(url).json()