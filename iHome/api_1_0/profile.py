# coding=utf-8
from . import api
from flask import session,current_app,jsonify,request,g
from iHome.models import User
from iHome.response_code import RET
from iHome import constants,db
from iHome.utils.image_stroage import image_storage
from iHome.utils.commons import login_required

@api.route('/user/auth',methods=['POST'])
@login_required
def set_user_auth():
    req_dict = request.json
    real_name = req_dict.get('real_name')
    id_card = req_dict.get('id_card')
    if not all([real_name,id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户信息失败')
    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')
    if user.real_name and user.id_card:
        return jsonify(errno=RET.DATAEXIST, errmsg='已经实名认证')

    user.real_name = real_name
    user.id_card = id_card

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='设置实名信息失败')
    return jsonify(errno=RET.OK, errmsg='实名认证成功')

@api.route('/user/name', methods=['PUT'])
@login_required
def set_user_name():
    req_dict = request.json
    username = req_dict.get('username')
    if not username:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户信息失败')
    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')

    user.name = username
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='设置用户名失败')
    return jsonify(errno=RET.OK, errmsg='设置用户名成功')

@api.route('/user/avatar', methods=['POST'])
@login_required
def save_user_avatar():
    file = request.files.get('avatar')
    if not file:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')
    try:
        key = image_storage(file.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传头像失败')
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户信息失败')
    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')
    user.avatar_url = key
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存头像记录失败')
    avatar_url = constants.QINIU_DOMIN_PREFIX + key
    return jsonify(errno=RET.OK, errmsg='上传头像成功',data={'avatar_url':avatar_url})


@api.route('/user')
@login_required
def get_user_info():
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户信息失败')

    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')


    return jsonify(errno=RET.OK, errmsg='ok',data=user.to_dict())