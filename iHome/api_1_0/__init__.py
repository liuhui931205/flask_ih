# coding=utf-8
from flask import Blueprint
api = Blueprint('api_1_0',__name__)

# from iHome.api_1_0 import index
from iHome.api_1_0.verify import get_image_code
from iHome.api_1_0.passport import register