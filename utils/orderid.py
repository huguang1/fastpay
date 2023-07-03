#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2019/5/28
import random


def generate_order_id(time):
    """
    生成20位本系统时间字符串+1位随机数
    :return: str
    """
    return time.strftime('%Y%m%d%H%M%S%f') + str(random.randint(0, 9))
