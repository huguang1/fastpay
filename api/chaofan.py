#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: June
# @Time : 2019/5/30
import hashlib
import requests
from urllib.parse import parse_qs


def service(domain, pay_code, amount, api, order_id, order_time, user_ip):
    # 回调、跳转url处理
    if api.notify_url:
        notify_url = api.notify_url
    else:
        notify_url = domain+'/pay/notify/'+api.payment_code
    if api.callback_url:
        callback_url = api.callback_url
    else:
        callback_url = domain+'/callback'
    arguments = {
        "service": pay_code,
        "version": "1.0",
        "merchantId": api.memberid,
        "orderNo": order_id,
        "tradeDate": order_time.strftime('%Y%m%d'),
        "tradeTime": order_time.strftime('%H%M%S'),
        "amount": int(amount*100),
        "clientIp": user_ip,
        "notifyUrl": notify_url,
        "merchantUrl": callback_url,
        "key": api.api_key
    }
    ordered_key = sorted(arguments)
    origin = "&".join(['%s=%s' % (i, arguments[i]) for i in ordered_key])
    obj = hashlib.md5()
    obj.update(origin.encode("utf-8"))
    secret = obj.hexdigest().lower()
    arguments["sign"] = secret
    arguments.pop('key')
    res = requests.post(api.http_url, data=arguments)
    res_data = dict([(k, v[0]) for k, v in parse_qs(res.text).items()])
    print(res_data)
    if res_data['repCode'] == '0001':
        return 'redirect.html', {"data": res_data["resultUrl"]}
    else:
        data = {
            "errorMsg": res_data["repMsg"]
        }
        return 'error.html', data


def notify(request):
    res_data = request.body
    print(res_data)
    print(type(res_data))
    return "SUCCESS"