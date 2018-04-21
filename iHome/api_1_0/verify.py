# coding=utf-8
from . import api
from iHome.utils.captcha.captcha import captcha
from flask import request, make_response, jsonify, current_app
from iHome import redis_store
from iHome import constants
from iHome.response_code import RET
import re
from iHome.utils.sms import CCP
import random
import json


@api.route('/sms_code', methods=['POST'])
def get_sms_code():
    req_data = request.data
    req_dict = json.loads(req_data)
    mobile = req_dict.get('mobile')
    image_code = req_dict.get('image_code')
    image_code_id = req_dict.get('image_code_id')

    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    if not re.match(r'1[3456789]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式不正确')
    try:
        real_code = redis_store.get('imagecode:%s' % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询图片验证码错误')

    if not real_code :
        return jsonify(errno=RET.NODATA, errmsg='图片验证码已过期')
    if real_code != image_code:
        return jsonify(errno=RET.DATAERR, errmsg='图片验证码错误')

    code = '%06d' % random.randint(0, 999999)
    current_app.logger.info('短信验证码：' + code)

    try:
        redis_store.set('smscode:%s' % mobile, code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存验证码失败')

    # res = CCP().sendtemplatesms(mobile, [code,  constants.SMS_CODE_REDIS_EXPIRES/60], 1)
    # if res != 1:
    #     return jsonify(errno=RET.THIRDERR, errmsg='发送短信失败')
    return jsonify(errno=RET.OK, errmsg='发送成功')


@api.route('/image_code')
def get_image_code():
    cur_id = request.args.get('cur_id')
    name, text, data = captcha.generate_captcha()
    current_app.logger.info('图片验证码：' + text)
    try:
        redis_store.set('imagecode:%s' % cur_id,text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存图片验证码失败')

    response = make_response(data)
    response.headers['Content-Type'] = 'image/jpg'
    return response
