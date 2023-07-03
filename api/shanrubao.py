#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: June
# @Time : 2019/5/29
import hashlib


def service(domain, pay_code, amount, api, order_id, **kwargs):
    # 回调、跳转url处理
    notify_url = ''
    callback_url = ''
    arguments = {
        "goodsname": "",
        "orderuid": "",
        "uid": api.memberid,
        "istype": pay_code,
        "price": str(amount),
        "orderid": order_id,
        "notify_url": notify_url,
        "return_url": callback_url,
        "version": 2,
        "token": api.api_key
    }
    ordered_key = sorted(arguments)
    origin = "&".join(['%s=%s' % (i, arguments[i]) for i in ordered_key])
    obj = hashlib.md5()
    obj.update(origin.encode("utf-8"))
    secret = obj.hexdigest().lower()
    arguments["key"] = secret
    arguments.pop('token')
    data = {
        "data": {
            'param': arguments,
            'url': api.http_url
        }
    }
    return 'form.html', data
