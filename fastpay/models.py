#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2019/5/28
from peewee import *
from datetime import datetime
from fastpay.settings import mysql_db


class BaseModel(Model):
    create_time = DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        database = mysql_db


class TDictionary(Model):
    """
    字典型数据表
    """
    dic_key = CharField(max_length=100, null=True)
    dic_value = CharField(max_length=2000, null=True)
    description = CharField(max_length=200, null=True)

    class Meta:
        db_table = 't_dictionary'
        database = mysql_db


class TGroup(BaseModel):
    """
    用户分组表
    """
    name = CharField(max_length=50, null=True, help_text="名称")
    state = IntegerField(null=True, help_text="状态")
    str_values = CharField(max_length=1000, null=True, help_text="分组值")
    remark = CharField(max_length=100, null=True, help_text="备注")
    create_user = CharField(max_length=20, null=True, help_text="创建人")
    update_user = CharField(max_length=20, null=True, help_text="更新人")
    update_time = DateTimeField(help_text="更新时间")

    class Meta:
        db_table = 't_group'


class TPayInfo(BaseModel):
    """
    支付通道
    """
    payment_code = CharField(max_length=20, null=True, help_text="平台编码")
    payment_name = CharField(max_length=50, null=True, help_text="平台名称")
    pay_code = CharField(max_length=255, null=True, help_text="方式编码")
    item_name = CharField(max_length=50, null=True, help_text="支付类型名称")
    item_code = CharField(max_length=50, null=True, help_text="支付类型编码")
    pay_model = IntegerField(help_text="支付设备")
    icon = CharField(max_length=255, null=True, help_text="图标")
    rate = DecimalField(max_digits=10, decimal_places=2, null=True, help_text="佣金比例/单笔佣金")
    rate_type = IntegerField(null=True, help_text="佣金类型")
    state = IntegerField(null=True, help_text="状态")
    min_switch = CharField(max_length=4, null=True, help_text="最小金额开关")
    min_amount = DecimalField(max_digits=11, decimal_places=2, null=True, help_text="最小金额")
    max_amount = DecimalField(max_digits=11, decimal_places=2, null=True, help_text="最大金额")
    max_switch = CharField(max_length=4, null=True, help_text="最大金额开关")
    point_switch = CharField(max_length=4, null=True, help_text="积分开关")
    bank_code = CharField(max_length=32, null=True, help_text="网银类型")
    create_user = CharField(max_length=20, null=True)
    update_user = CharField(max_length=20, null=True)
    udpate_time = TimestampField()

    class Meta:
        db_table = 't_pay_info'


class TPayApi(BaseModel):
    """
    平台接口参数表
    """
    payment_code = CharField(unique=True, max_length=20, null=True)
    payment_name = CharField(max_length=50, null=True)
    state = IntegerField(null=True)
    memberid = CharField(max_length=50, null=True)
    api_key = CharField(max_length=2000, null=True)
    http_url = CharField(max_length=100, null=True)
    http_type = CharField(max_length=10, null=True)
    notify_url = CharField(max_length=100, null=True)
    notify_type = CharField(max_length=16, null=True)
    callback_url = CharField(max_length=100, null=True)
    query_url = CharField(max_length=100, null=True)
    sign_type = CharField(max_length=50, null=True)
    sign_format = CharField(max_length=2000, null=True)
    param_format = CharField(max_length=2000, null=True)
    verify_format = CharField(max_length=2000, null=True)
    remark = CharField(max_length=200, null=True)
    attribute_1 = CharField(max_length=400, null=True)
    attribute_2 = CharField(max_length=400, null=True)
    attribute_3 = CharField(max_length=1000, null=True)
    attribute_4 = CharField(max_length=2000, null=True)
    attribute_5 = CharField(max_length=2000, null=True)
    create_user = CharField(max_length=20, null=True)
    update_user = CharField(max_length=20, null=True)
    udpate_time = DateTimeField()

    class Meta:
        db_table = 't_pay_api'


class TLookupItem(BaseModel):
    """
    
    """
    item_code = CharField(max_length=20, null=True)
    item_name = CharField(max_length=50, null=True)
    sort = IntegerField(null=True)
    state = IntegerField(null=True)
    group_code = CharField(max_length=20, null=True)
    parent_item_code = CharField(max_length=20, null=True)
    attribute_1 = CharField(max_length=100, null=True)
    attribute_2 = CharField(max_length=100, null=True)
    attribute_3 = CharField(max_length=100, null=True)
    attribute_4 = CharField(max_length=100, null=True)
    attribute_5 = CharField(max_length=100, null=True)
    create_user = CharField(max_length=20, null=True)
    update_user = CharField(max_length=20, null=True)
    udpate_time = DateTimeField()

    class Meta:
        db_table = "t_lookup_item"


class TCustomerUser(BaseModel):
    """
    用户表
    """
    user_account = CharField(unique=True, max_length=20, null=True)
    level = IntegerField(null=True, help_text="级别")
    amounts = DecimalField(max_digits=13, decimal_places=2, null=True, help_text="累计总额")
    group_id = IntegerField(null=True, help_text="分组id")
    remark = CharField(max_length=255, null=True, help_text="备注")
    update_time = DateTimeField()

    class Meta:
        db_table = 't_customer_user'


class TOrder(BaseModel):
    """
    订单表
    """
    user_account = CharField(max_length=20, null=True)
    order_id = CharField(unique=True, max_length=255, null=True)
    order_amount = DecimalField(max_digits=10, decimal_places=2, null=True)
    order_state = IntegerField(null=True, help_text="支付状态")
    order_desc = CharField(max_length=255, null=True)
    order_time = DateTimeField(null=True)
    user_ip = CharField(max_length=50, null=True)
    payment_code = CharField(max_length=255, null=True)
    pay_code = CharField(max_length=100, null=True)
    pay_order = CharField(max_length=255, null=True)
    item_code = CharField(max_length=255, null=True)
    state = IntegerField(null=True, help_text="订单操作状态")
    rate = DecimalField(max_digits=10, decimal_places=2, null=True)
    rate_amount = DecimalField(max_digits=10, decimal_places=2, null=True)
    lock_id = CharField(max_length=20, null=True)
    external_id = IntegerField(null=True)
    update_time = DateTimeField(null=True)
    update_user = CharField(max_length=30, null=True)

    class Meta:
        db_table = 't_order'


class WhiteBlackList(BaseModel):
    """
    黑白名单，前台黑名单、后台白名单
    """
    ip = CharField(max_length=255, null=True)
    user_name = CharField(max_length=255, null=True)
    role_type = IntegerField(null=True)
    remarks = CharField(max_length=255, null=True)
    create_user = CharField(max_length=255, null=True)
    update_time = DateTimeField(null=True)
    update_user = CharField(max_length=255, null=True)

    class Meta:
        db_table = 'white_black_list'
