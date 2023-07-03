#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: June
# @Time : 2019/5/31
import hashlib
from decimal import Decimal

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
    params = {
        "customer": api.memberid,
        "banktype": pay_code,
        "amount": str(amount.quantize(Decimal('0.00'))),
        "orderid": order_id,
        "asynbackurl": notify_url,
        "request_time": order_time.strftime("%Y%m%d%H%M%S"),
        "key": api.api_key
    }
    origin = "&".join([i + "=" + params[i] for i in params])
    obj = hashlib.md5()
    obj.update(origin.encode("utf-8"))
    secret = obj.hexdigest().lower()
    params["sign"] = secret
    params["synbackurl"] = callback_url
    params.pop('key')
    data = {
        "data": {
            'param': params,
            'url': api.http_url
        }
    }
    return 'form.html', data


def notify(request):
    res_data = request.body
    print(res_data)
    print(type(res_data))
    return "SUCCESS"