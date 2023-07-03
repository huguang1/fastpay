#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2019/5/27
from tornado.web import url
from fastpay.handler import *
urlpattern = [
    url(r"/pay/getValueByKey/(.+)", DictHandler),
    url(r"/pay/getPayType", PayTypeHandler),
    url(r"/pay/getPayTypeLimit", PayLimitHandler),
    url(r"/pay/server", PayServerHandler),
    url(r"/pay/notify/(.+)", NotifyHandler),
    url(r"/pay/callback", CallbackHandler),
    url(r"/test", TestHandler),
]
