# coding=utf-8
from flask import Blueprint,current_app

html = Blueprint('html',__name__)
@html.route('/<re(".*"):file_name>')
def index(file_name):
    if file_name == '':
        file_name = 'index.html'
    if file_name != 'favicon.ico':
        file_name = 'html/' + file_name

    return current_app.send_static_file(file_name)
