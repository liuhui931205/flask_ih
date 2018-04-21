# coding=utf-8
from werkzeug.routing import BaseConverter
from flask import session,jsonify,g
from iHome.response_code import RET
import functools

class RegexConverter(BaseConverter):

    def __init__(self,url_map,regex):
        super(RegexConverter,self).__init__(url_map)
        self.regex = regex

def login_required(func):
    @functools.wraps(func)
    def wapper(*args,**kwargs):
        user_id = session.get('user_id')
        if user_id:
            g.user_id = user_id
            return func(*args, **kwargs)
        else:
            # 用户未登录
            return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')

    return wapper
