# coding=utf-8
from datetime import datetime

from . import api
from flask import current_app, g, request, jsonify, session
from iHome.response_code import RET
from iHome.models import Area, House, Facility, HouseImage, Order
from iHome.utils.commons import login_required
from iHome.utils.image_stroage import image_storage
from iHome import db, redis_store
from iHome import constants
import json


@api.route('/houses')
def get_houses_list():
    # print request.args
    area_id = request.args.get('aid')
    sort_key = request.args.get('sk', 'new')
    page = request.args.get('p')
    sd = request.args.get('sd')
    ed = request.args.get('ed')

    start_date = None
    end_date = None

    try:
        if area_id:
            area_id = int(area_id)
        page = int(page)
        if sd:
            start_date = datetime.strptime(sd, '%Y-%m-%d')
        if ed:
            end_date = datetime.strptime(ed, '%Y-%m-%d')
        if start_date and end_date:
            assert start_date < end_date, Exception('起始时间大于结束时间')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    try:
        key = 'house:%s:%s:%s:%s' % (area_id, sd, ed, sort_key)
        res_json_str = redis_store.hget(key,page)
        if res_json_str:
            resp = json.loads(res_json_str)
            return jsonify(errno=RET.OK, errmsg='OK', data=resp)
    except Exception as e:
        current_app.logger.error(e)
    try:
        # houses = House.query.all()
        houses_query = House.query
        if area_id:
            houses_query = houses_query.filter(House.area_id == area_id)
        try:
            conflict_order_li = []
            if start_date and end_date:
                conflict_order_li = Order.query.filter(end_date > Order.begin_date, start_date < Order.end_date).all()
            elif start_date:
                conflict_order_li = Order.query.filter(start_date < Order.end_date).all()
            elif end_date:
                conflict_order_li = Order.query.filter(end_date > Order.begin_date).all()
            if conflict_order_li:
                conflict_house_id = [order.house_id for order in conflict_order_li]
                houses_query = House.query.filter(House.id.notin_(conflict_house_id))
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='查询冲突订单失败')

        if sort_key == 'price-inc':
            houses_query = houses_query.order_by(House.price)
        elif sort_key == 'booking':
            houses_query = houses_query.order_by(House.order_count.desc())
        elif sort_key == 'price-des':
            houses_query = houses_query.order_by(House.price.desc())
        else:
            houses_query = houses_query.order_by(House.create_time.desc())

        houses_paginate = houses_query.paginate(page, constants.HOUSE_LIST_PAGE_CAPACITY, False)
        houses = houses_paginate.items
        total_page = houses_paginate.pages



    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋信息失败')

    house_dict_li = []
    for house in houses:
        house_dict_li.append(house.to_basic_dict())

    resp = {'houses': house_dict_li, 'total_page': total_page}
    try:
        key = 'house:%s:%s:%s:%s' % (area_id, sd, ed, sort_key)
        pipeline = redis_store.pipeline()
        pipeline.multi()
        pipeline.hset(key, page, json.dumps(resp))
        pipeline.expire(key, constants.HOUSE_LIST_REDIS_EXPIRES)
        pipeline.execute()
    except Exception as e:
        current_app.logger.error(e)

    return jsonify(errno=RET.OK, errmsg='ok', data=resp)


@api.route('/houses/index')
def get_houses_index():
    try:
        houses = House.query.order_by(House.create_time.desc()).limit(5).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取房屋信息失败')
    houses_dict_li = []
    for house in houses:
        houses_dict_li.append(house.to_basic_dict())
    return jsonify(errno=RET.OK, errmsg='ok', data=houses_dict_li)


@api.route('/house/<int:house_id>')
def get_house_info(house_id):
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋信息失败')
    if not house:
        return jsonify(errno=RET.NODATA, errmsg='房屋不存在')
    user_id = session.get('user_id', -1)
    return jsonify(errno=RET.OK, errmsg='OK', data={'house': house.to_full_dict(), 'user_id': user_id})


@api.route('/houses/image', methods=['POST'])
@login_required
def save_house_image():
    house_id = request.form.get('house_id')
    if not house_id:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

    file = request.files.get('house_image')
    if not file:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋信息失败')

    if not house:
        return jsonify(errno=RET.NODATA, errmsg='房屋不存在')
    try:
        key = image_storage(file.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传房屋图片失败')
    house_image = HouseImage()
    house_image.house_id = house_id
    house_image.url = key

    if not house.index_image_url:
        house.index_image_url = key

    try:
        db.session.add(house_image)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存房屋图片信息失败')

    img_url = constants.QINIU_DOMIN_PREFIX + key
    return jsonify(errno=RET.OK, errmsg='OK', data={'img_url': img_url})


@api.route('/houses', methods=["POST"])
@login_required
def save_new_house():
    req_dict = request.json
    title = req_dict.get('title')
    price = req_dict.get('price')  # 房屋价格
    address = req_dict.get('address')
    area_id = req_dict.get('area_id')
    room_count = req_dict.get('room_count')
    acreage = req_dict.get('acreage')
    unit = req_dict.get('unit')
    capacity = req_dict.get('capacity')
    beds = req_dict.get('beds')
    deposit = req_dict.get('deposit')  # 房屋押金
    min_days = req_dict.get('min_days')
    max_days = req_dict.get('max_days')

    if not all(
            [title, price, address, area_id, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    try:
        price = float(price) * 100
        deposit = float(deposit) * 100
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    house = House()
    house.user_id = g.user_id
    house.area_id = area_id
    house.title = title
    house.price = price
    house.address = address
    house.room_count = room_count
    house.acreage = acreage
    house.unit = unit
    house.capacity = capacity
    house.beds = beds
    house.deposit = deposit
    house.min_days = min_days
    house.max_days = max_days
    facility = req_dict.get('facility')
    try:
        facilities = Facility.query.filter(Facility.id.in_(facility)).all()
        if facilities:
            house.facilities = facilities
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取房屋设施信息失败')

        # 3. 将房屋的基本信息添加进数据库
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存房屋信息失败')

        # 4. 返回应答
    return jsonify(errno=RET.OK, errmsg='OK', data={'house_id': house.id})


@api.route('/areas')
def get_areas():
    try:
        area_json_str = redis_store.get('areas')
        if area_json_str:
            areas_dict_li = json.loads(area_json_str)
            return jsonify(errno=RET.OK, errmsg='ok', data=areas_dict_li)
    except Exception as e:
        current_app.logger.error(e)

    try:
        areas = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询地区失败')
    areas_dict_li = []
    for area in areas:
        areas_dict_li.append(area.to_dict())
    try:
        redis_store.set('areas', json.dumps(areas_dict_li), constants.AREA_INFO_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
    return jsonify(errno=RET.OK, errmsg='ok', data=areas_dict_li)
