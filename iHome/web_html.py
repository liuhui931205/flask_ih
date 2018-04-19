# coding=utf-8
from flask import Blueprint,current_app,make_response
from flask_wtf.csrf import generate_csrf

html = Blueprint('html',__name__)
@html.route('/<re(".*"):file_name>')
def index(file_name):
    if file_name == '':
        file_name = 'index.html'
    if file_name != 'favicon.ico':
        file_name = 'html/' + file_name

    response = make_response(current_app.send_static_file(file_name))

    response.set_cookie('csrf_token',generate_csrf())
    return response
