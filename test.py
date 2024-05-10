# import okx.Account as Account
# import okx.Trade as trade
# import pprint
# api_key='43f5df59-5e61-4d24-875e-f32c003e0430'
# secret_key='5B1063B322635A27CF01BACE3772E0E0'
# passphrase='Parkwood270298)'
# flag = "1"  # live trading: 0, demo trading: 1
# accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
# tradeAPI = trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
# # result = tradeAPI.place_order(
# #     instId="ETH-USDT-SWAP",
# #     tdMode="isolated",
# #     side="buy",
# #     posSide="long",
# #     ordType="market",
# #     sz="1"
# # )
# # print(result)
# # ordI=result["data"][0]["ordId"]
# ordI=1437244935699087360
# resul= tradeAPI.cancel_order(instId="ETH-USDT-SWAP", ordId=ordI)
# print(resul)




