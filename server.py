#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2019/5/27
import os
import redis
from tornado import web, ioloop
from peewee_async import Manager
from tornado.options import define, options

define("debug", default=True, help="false or 0 is False,others are Ture", type=bool)
define("port", default=8000, help="run on the given port", type=int)
define("db_host", default="192.168.29.165", help="mysql host")
define("db_port", default=3306, help="mysql port", type=int)
define("db_database", default="fast_recharge", help="mysql database")
define("db_user", default="root", help="mysql user")
define("db_pwd", default="Hdug&34dg1Gd", help="mysql password")
define("db_min", default=1, help="min_connections", type=int)
define("db_max", default=10, help="max_connections", type=int)
define("rd_host", default="192.168.29.165", help="redis host")
define("rd_port", default=6379, help="redis port", type=int)
define("rd_db", default=6, help="select redis db", type=int)
define("rd_pwd", default="", help="redis password")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Application(web.Application):
    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)
        rdp = redis.ConnectionPool(
            host=options.rd_host,
            port=options.rd_port,
            db=options.rd_db,
            password=options.rd_pwd,
            decode_responses=True,
        )
        self.redis = redis.StrictRedis(connection_pool=rdp)


if __name__ == '__main__':
    options.log_file_prefix = os.path.join(BASE_DIR, 'logs/fastpay.log')
    options.logging = "debug"
    options.parse_command_line()
    from fastpay.urls import urlpattern
    app = Application(
        urlpattern,
        debug=options.debug,
        template_path=os.path.join(BASE_DIR, 'templates'),
        static_path=os.path.join(BASE_DIR, 'statics'),
    )
    app.listen(options.port)
    from fastpay.settings import mysql_db as db
    objects = Manager(db)
    db.set_allow_sync(False)
    app.objects = objects
    ioloop.IOLoop.current().start()
