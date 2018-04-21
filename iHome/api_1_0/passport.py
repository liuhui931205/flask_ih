# coding=utf-8
from . import api
from flask import request,jsonify,current_app,session
from iHome.response_code import RET
from iHome import redis_store,db
from iHome.models import User
import re

@api.route('/session',methods=['DELETE'])
def logout():
    session.clear()
    return jsonify(errno=RET.OK, errmsg='退出登录成功')

@api.route('/session',methods=['POST'])
def login():
    req_dict = request.json
    mobile = req_dict.get('mobile')
    password = req_dict.get('password')

    if not all([mobile,password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    if not re.match(r'1[3456789]\d{9}',mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式不正确')

    try:
        user = User.query.filter(User.mobile==mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户错误')
    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')

    if not user.check_user_password(password):
        return jsonify(errno=RET.PWDERR, errmsg='密码错误')

    session['user_id'] = user.id
    session['username'] = user.name
    session['mobile'] = user.mobile

    return jsonify(errno=RET.OK, errmsg='登录成功')


@api.route('/users',methods=['POST'])
def register():
    req_dict = request.json
    mobile = req_dict.get('mobile')
    phonecode = req_dict.get('phonecode')
    password = req_dict.get('password')

    if not all([mobile, phonecode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    try:
        code = redis_store.get('smscode:%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询短信验证码失败')

    if not code:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码已过期')

    if code != phonecode:
        return jsonify(errno=RET.DATAERR, errmsg='短信验证码错误')
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        if user:
            return jsonify(errno=RET.DATAEXIST, errmsg='用户已存在')

    user = User()
    user.mobile = mobile
    user.name = mobile
    # todo 密码加密
    user.password = password

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存用户信息失败')

    session['user_id'] = user.id
    session['username'] = user.name
    session['mobile'] = user.mobile

    return jsonify(errno=RET.OK, errmsg='注册成功')
