#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2019/5/28
from tornado.options import options
import peewee_async
mysql_db = peewee_async.PooledMySQLDatabase(
    options.db_database,
    host=options.db_host,
    port=options.db_port,
    user=options.db_user,
    password=options.db_pwd,
    min_connections=options.db_min,
    max_connections=options.db_max
)
