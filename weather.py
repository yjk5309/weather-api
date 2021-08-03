import pymysql
from flask import Flask, Blueprint, jsonify, request, render_template
from flask_restful import reqparse, abort, Api, Resource
import requests
import json

from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required

weather = Blueprint('weather', __name__)
api = Api(weather)

from config import API_KEY

db = pymysql.connect(
        user = 'root',
        host = '127.0.0.1',
        port = 3306,
        db = 'weather',
        charset = 'utf8'
    )
cursor = db.cursor()

parser = reqparse.RequestParser()
parser.add_argument('city_name')
parser.add_argument('reason')


"""
Weather APIs - 날씨 정보를 알고싶은 도시 CRUD

Create API : city name을 입력받아 날씨 정보를 알고싶은 도시와 그 이유를 등록합니다.
Read API : 현재 등록된 도시의 이름과 날씨를 가져옵니다.
Update API : 기존에 있는 도시를 선택한 이유를 변경합니다.
Delete API : 특정 도시를 제거합니다.
"""
@weather.route('/weather', methods=['GET'])
@jwt_required()
def get():
    user = get_jwt_identity()
    sql = "SELECT id, city_name, reason FROM `city` where user_id = %s"
    cursor.execute(sql, (user))
    cites = cursor.fetchall()
    api_key = API_KEY

    weather = []
    for i in cites:
        api_url = f'https://api.openweathermap.org/data/2.5/weather?q={i[1]}&appid={api_key}&lang=kr'
        response = requests.get(api_url)
        data = json.loads(response.text)
        city = {"city" : i[1], "weather" : data['weather'][0]['description'], "reason" : i[2]}
        weather.append(city)

    # return render_template('home.html', result = weather)
    return jsonify(status = 200, result = weather)

@weather.route('/weather', methods=['POST'])
@jwt_required()
def post():
    args = parser.parse_args()
    user = get_jwt_identity()
    sql = "INSERT INTO `city` (`city_name`, `reason`, `user_id`) VALUES (%s, %s, %s)"
    cursor.execute(sql, (args['city_name'], args['reason'], user))
    db.commit()
    
    
    # return jsonify(status = 200, result = {"city_name": args["city_name"], "reason": args["reason"]})
    get_sql = "SELECT id, city_name, reason FROM `city` where user_id = %s"
    cursor.execute(get_sql, (user))
    cites = cursor.fetchall()
    api_key = API_KEY

    weather = []
    for i in cites:
        api_url = f'https://api.openweathermap.org/data/2.5/weather?q={i[1]}&appid={api_key}&lang=kr'
        response = requests.get(api_url)
        data = json.loads(response.text)
        city = {"city" : i[1], "weather" : data['weather'][0]['description'], "reason" : i[2]}
        weather.append(city)

    # return render_template('home.html', result = weather)
    return jsonify(status = 200, result = weather)
    # 실행된 후 프론트에서 get으로 redirect -> 추가된 나라의 날씨까지 보임

@weather.route('/weather', methods=['PUT'])
@jwt_required()
def put():
    args = parser.parse_args()
    user = get_jwt_identity()
    sql = "UPDATE `city` SET reason = %s WHERE `city_name` = %s and user_id = %s"
    cursor.execute(sql, (args['reason'], args["city_name"], user))
    db.commit()
    
    # return jsonify(status = "success", result = {"reason": args["reason"], "city_name": args["city_name"]})
    get_sql = "SELECT id, city_name, reason FROM `city` where user_id = %s"
    cursor.execute(get_sql, (user))
    cites = cursor.fetchall()
    api_key = API_KEY

    weather = []
    for i in cites:
        api_url = f'https://api.openweathermap.org/data/2.5/weather?q={i[1]}&appid={api_key}&lang=kr'
        response = requests.get(api_url)
        data = json.loads(response.text)
        city = {"city" : i[1], "weather" : data['weather'][0]['description'], "reason" : i[2]}
        weather.append(city)

    # return render_template('home.html', result = weather)
    return jsonify(status = 200, result = weather)

@weather.route('/weather', methods=['DELETE'])
@jwt_required()
def delete():
    args = parser.parse_args()
    user = get_jwt_identity()
    sql = "DELETE FROM `city` WHERE `city_name` = %s and user_id = %s"
    cursor.execute(sql, (args["city_name"], user))
    db.commit()
    
    # return jsonify(status = "success", result = {"city_name": args["city_name"]})
        # 실행된 후 프론트에서 get으로 redirect -> 삭제한 나라의 날씨 보이지 않음
    get_sql = "SELECT id, city_name, reason FROM `city` where user_id = %s"
    cursor.execute(get_sql, (user))
    cites = cursor.fetchall()
    api_key = API_KEY

    weather = []
    for i in cites:
        api_url = f'https://api.openweathermap.org/data/2.5/weather?q={i[1]}&appid={api_key}&lang=kr'
        response = requests.get(api_url)
        data = json.loads(response.text)
        city = {"city" : i[1], "weather" : data['weather'][0]['description'], "reason" : i[2]}
        weather.append(city)

    return render_template('home.html', result = weather)

# api.add_resource(Weather, '/weather')
