#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2019/5/28
import json
import importlib
from utils.json import CJsonEncoder
from tornado.web import RequestHandler
from playhouse.shortcuts import model_to_dict
from constants import Constants
from fastpay.models import *
from utils.orderid import generate_order_id
from decimal import Decimal
import random


class BaseHandler(RequestHandler):
    @property
    def redis_conn(self):
        return self.application.redis

    def set_default_headers(self) -> None:
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Content-type', '*/*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, PATCH, OPTIONS')
        self.set_header(
            'Access-Control-Allow-Headers',
            'Content-Type, tsessionid, Access-Control-Allow-Origin,'
            'Access-Control-Allow-Headers, X-Requested-By, Access-Control-Allow-Methods'
        )

class DictHandler(BaseHandler):
    """
    根据key查询数据库字典
    """
    async def get(self, key):
        self.set_header("Content-Type", "application/text")
        value = self.redis_conn.get(Constants["REDIS_DICTIONARY_ITEM"]+key)
        if value is not None:
            self.write(value)
        else:
            try:
                value = await self.application.objects.get(TDictionary, dic_key=key)
                self.redis_conn.set(Constants["REDIS_DICTIONARY_ITEM"]+key, value.dic_value, 60*30)
                await self.finish(value.dic_value)
            except TDictionary.DoesNotExist:
                await self.finish('')


class PayTypeHandler(BaseHandler):
    """
    获取首页默认支付通道
    """
    async def get(self):
        self.set_header("Content-Type", "application/json")
        res = self.redis_conn.get(Constants["REDIS_FIRST_GROUP_PAYINFO_DATA"])
        if res is not None:
            pay_list = json.loads(res)
        else:
            try:
                res = await self.application.objects.get(TGroup, id=1)
                info_ids = []
                for i in json.loads(res.str_values).values():
                    info_ids.append(int(i.split('&')[2]))
                pay_infos = list(await self.application.objects.execute(TPayInfo.select().where(TPayInfo.id.in_(info_ids))))
                # 按照info_ids里的顺序进行排序
                temp = {i.id: i for i in pay_infos}
                sorted_pay_infos = [temp[j] for j in info_ids]
                pay_list = [model_to_dict(k) for k in sorted_pay_infos]
            except TGroup.DoesNotExist:
                pay_list = []
            pay_list_json = json.dumps(pay_list, cls=CJsonEncoder)
            self.redis_conn.set(Constants["REDIS_FIRST_GROUP_PAYINFO_DATA"], pay_list_json, 60*10)
        content = {
            "code": "200",
            "data": pay_list,
            "message": "操作成功"
        }
        content = json.dumps(content, cls=CJsonEncoder)
        return await self.finish(content)


class PayLimitHandler(BaseHandler):
    """
    根据所选支付方式获得所配置的支付通道的金额限制
    """
    async def get(self):
        self.set_header("Content-Type", "application/text")
        pay_type = self.get_argument('payType', None)
        if pay_type is not None:
            try:
                pay_limit = await self.application.objects.get(TLookupItem, item_code=pay_type)
                limit_min, limit_max = pay_limit.attribute_2 or 10, pay_limit.attribute_3 or 50000
                await self.finish('{},{}'.format(limit_min, limit_max))
            except TLookupItem.DoesNotExist:
                await self.finish("10,50000")
        else:
            await self.finish("10,50000")


class PayServerHandler(BaseHandler):
    """
    处理提交的订单
    """
    async def post(self):
        name = self.get_argument('username', None)
        backcode = self.get_argument('backcode', None)
        amount = self.get_argument('amount', None)
        userIp = self.get_argument('userIp', None)
        domain = self.request.protocol + "://" + self.request.host
        if not all([name, backcode, amount, userIp]):
            return await self.render('error.html', errorMsg="提交参数不完整！")
        # redis限流、黑名单效验
        limits = self.redis_conn.get(Constants["REDIS_REQ_LIMIT"]+name)
        if limits:
            return await self.render('error.html', errorMsg="不可频繁提交")
        else:
            self.redis_conn.set(Constants["REDIS_REQ_LIMIT"] + name, 1, ex=30)
        black = await self.application.objects.count(WhiteBlackList.select().where((WhiteBlackList.ip == userIp or WhiteBlackList.user_name == name) and WhiteBlackList.role_type == 1))
        if black > 0:
            return await self.render('error.html', errorMsg="用户受限")
        # 根据用户名查所属组、根据支付方式查支付通道
        try:
            user = await self.application.objects.get(TCustomerUser, user_account=name)
            groupId = user.group_id
        except TCustomerUser.DoesNotExist:
            groupId = 1
        try:
            group = await self.application.objects.get(TGroup, id=groupId)
            payInfoId = json.loads(group.str_values)[backcode].split('&')[2]
            payInfo = await self.application.objects.get(TPayInfo, id=payInfoId)
            if payInfo.payment_code == '' or payInfo.pay_code == '' or 'weihu' in payInfo.payment_code:
                return await self.render('error.html', errorMsg="支付通道维护中。。。")
        except Exception as e:
            return await self.render('error.html', errorMsg="支付通道关闭")
        # 金额限制、处理
        amount = Decimal(amount)  # 全局转成Decimal
        if payInfo.min_switch and payInfo.min_switch.upper() == "ON" and amount < Decimal(payInfo.min_switch):
            return self.render("error.html", errorMsg=f"充值金额限制最少{payInfo.min_switch}")
        if payInfo.max_amount and payInfo.max_amount.upper() == "ON" and amount > Decimal(payInfo.max_amount):
            return self.render("error.html", errorMsg=f"充值金额限制最大{payInfo.max_amount}")
        if payInfo.point_switch and payInfo.point_switch.upper() == "ON":
            amount += (Decimal(random.randint(1, 20)) if random.randint(0, 100) < 80 else Decimal(random.randint(20, 100)))/Decimal('100')
        # 生成手续费
        if payInfo.rate_type == 2:
            rate = payInfo.rate
        else:
            rate = amount*payInfo.rate.quantize(Decimal('0.00'))
        # 生成订单
        order_time = datetime.now()
        order_id = generate_order_id(order_time)
        await self.application.objects.create(
            TOrder,
            user_account=name,
            order_id=order_id,
            order_amount=amount,
            order_state=10,  # 待处理
            order_time=order_time,
            user_ip=userIp,
            payment_code=payInfo.payment_code,
            pay_code=payInfo.pay_code,
            item_code=payInfo.item_code,
            state=10,
            rate=payInfo.rate,
            rate_amount=rate,
        )
        payApi = await self.application.objects.get(TPayApi, payment_code=payInfo.payment_code)
        module_name = "api.%s" % payInfo.payment_code
        api = importlib.import_module(module_name)
        template, data = api.service(domain=domain,pay_code=payInfo.pay_code, amount=amount, api=payApi, order_id=order_id, order_time=order_time, user_ip=userIp)
        await self.render(template, **data)


class NotifyHandler(BaseHandler):
    """
    服务器回调接口
    """
    async def post(self, payment_code):
        module_name = "apps.api.%s" % payment_code
        api = importlib.import_module(module_name)
        res = api.notify(self.request)
        return await self.finish(res)

    async def get(self, payment_code):
        module_name = "apps.api.%s" % payment_code
        api = importlib.import_module(module_name)
        res = api.notify(self.request)
        return await self.finish(res)


class CallbackHandler(BaseHandler):
    """
    前台跳转链接处理
    """
    def get(self):
        res = self.request.query
        return self.render("callback.html", state=30)


class TestHandler(BaseHandler):

    def options(self):
        self.write('')

    def post(self):
        data = {"code":0,"msg":"","count":1000,"data":[{"id":10000,"username":"user-0","sex":"女","city":"城市-0","sign":"签名-0","experience":255,"logins":24,"wealth":82830700,"classify":"作家","score":57},{"id":10001,"username":"user-1","sex":"男","city":"城市-1","sign":"签名-1","experience":884,"logins":58,"wealth":64928690,"classify":"词人","score":27},{"id":10002,"username":"user-2","sex":"女","city":"城市-2","sign":"签名-2","experience":650,"logins":77,"wealth":6298078,"classify":"酱油","score":31},{"id":10003,"username":"user-3","sex":"女","city":"城市-3","sign":"签名-3","experience":362,"logins":157,"wealth":37117017,"classify":"诗人","score":68},{"id":10004,"username":"user-4","sex":"男","city":"城市-4","sign":"签名-4","experience":807,"logins":51,"wealth":76263262,"classify":"作家","score":6},{"id":10005,"username":"user-5","sex":"女","city":"城市-5","sign":"签名-5","experience":173,"logins":68,"wealth":60344147,"classify":"作家","score":87},{"id":10006,"username":"user-6","sex":"女","city":"城市-6","sign":"签名-6","experience":982,"logins":37,"wealth":57768166,"classify":"作家","score":34},{"id":10007,"username":"user-7","sex":"男","city":"城市-7","sign":"签名-7","experience":727,"logins":150,"wealth":82030578,"classify":"作家","score":28},{"id":10008,"username":"user-8","sex":"男","city":"城市-8","sign":"签名-8","experience":951,"logins":133,"wealth":16503371,"classify":"词人","score":14},{"id":10009,"username":"user-9","sex":"女","city":"城市-9","sign":"签名-9","experience":484,"logins":25,"wealth":86801934,"classify":"词人","score":75},{"id":10010,"username":"user-10","sex":"女","city":"城市-10","sign":"签名-10","experience":1016,"logins":182,"wealth":71294671,"classify":"诗人","score":34},{"id":10011,"username":"user-11","sex":"女","city":"城市-11","sign":"签名-11","experience":492,"logins":107,"wealth":8062783,"classify":"诗人","score":6},{"id":10012,"username":"user-12","sex":"女","city":"城市-12","sign":"签名-12","experience":106,"logins":176,"wealth":42622704,"classify":"词人","score":54},{"id":10013,"username":"user-13","sex":"男","city":"城市-13","sign":"签名-13","experience":1047,"logins":94,"wealth":59508583,"classify":"诗人","score":63},{"id":10014,"username":"user-14","sex":"男","city":"城市-14","sign":"签名-14","experience":873,"logins":116,"wealth":72549912,"classify":"词人","score":8},{"id":10015,"username":"user-15","sex":"女","city":"城市-15","sign":"签名-15","experience":1068,"logins":27,"wealth":52737025,"classify":"作家","score":28},{"id":10016,"username":"user-16","sex":"女","city":"城市-16","sign":"签名-16","experience":862,"logins":168,"wealth":37069775,"classify":"酱油","score":86},{"id":10017,"username":"user-17","sex":"女","city":"城市-17","sign":"签名-17","experience":1060,"logins":187,"wealth":66099525,"classify":"作家","score":69},{"id":10018,"username":"user-18","sex":"女","city":"城市-18","sign":"签名-18","experience":866,"logins":88,"wealth":81722326,"classify":"词人","score":74},{"id":10019,"username":"user-19","sex":"女","city":"城市-19","sign":"签名-19","experience":682,"logins":106,"wealth":68647362,"classify":"词人","score":51},{"id":10020,"username":"user-20","sex":"男","city":"城市-20","sign":"签名-20","experience":770,"logins":24,"wealth":92420248,"classify":"诗人","score":87},{"id":10021,"username":"user-21","sex":"男","city":"城市-21","sign":"签名-21","experience":184,"logins":131,"wealth":71566045,"classify":"词人","score":99},{"id":10022,"username":"user-22","sex":"男","city":"城市-22","sign":"签名-22","experience":739,"logins":152,"wealth":60907929,"classify":"作家","score":18},{"id":10023,"username":"user-23","sex":"女","city":"城市-23","sign":"签名-23","experience":127,"logins":82,"wealth":14765943,"classify":"作家","score":30},{"id":10024,"username":"user-24","sex":"女","city":"城市-24","sign":"签名-24","experience":212,"logins":133,"wealth":59011052,"classify":"词人","score":76},{"id":10025,"username":"user-25","sex":"女","city":"城市-25","sign":"签名-25","experience":938,"logins":182,"wealth":91183097,"classify":"作家","score":69},{"id":10026,"username":"user-26","sex":"男","city":"城市-26","sign":"签名-26","experience":978,"logins":7,"wealth":48008413,"classify":"作家","score":65},{"id":10027,"username":"user-27","sex":"女","city":"城市-27","sign":"签名-27","experience":371,"logins":44,"wealth":64419691,"classify":"诗人","score":60},{"id":10028,"username":"user-28","sex":"女","city":"城市-28","sign":"签名-28","experience":977,"logins":21,"wealth":75935022,"classify":"作家","score":37},{"id":10029,"username":"user-29","sex":"男","city":"城市-29","sign":"签名-29","experience":647,"logins":107,"wealth":97450636,"classify":"酱油","score":27}]}
        return self.finish(data)