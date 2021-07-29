import pymysql
from flask import Flask, jsonify, request
from flask_restful import reqparse, abort, Api, Resource
import requests
import json

app = Flask(__name__)
api = Api(app)


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
class Weather(Resource):
    def get(self):
        sql = "SELECT id, city_name, reason FROM `city`"
        cursor.execute(sql)
        cites = cursor.fetchall()
        api_key = '8dd9ced94d21d217609afb007b1792c5'

        weather = []
        for i in cites:
            print(i[1])
            api_url = f'https://api.openweathermap.org/data/2.5/weather?q={i[1]}&appid={api_key}&lang=kr'
            response = requests.get(api_url)
            data = json.loads(response.text)
            city = {"city" : i[1], "weather" : data['weather'][0]['description'], "reason" : i[2]}
            weather.append(city)

        return jsonify(status = 200, result = weather)
        
    
    def post(self):
        args = parser.parse_args()
        sql = "INSERT INTO `city` (`city_name`, `reason`) VALUES (%s, %s)"
        cursor.execute(sql, (args['city_name'], args['reason']))
        db.commit()
        
        return jsonify(status = 200, result = {"city_name": args["city_name"], "reason": args["reason"]})
        # 실행된 후 프론트에서 get으로 redirect -> 추가된 나라의 날씨까지 보임
        
    def put(self):
        args = parser.parse_args()
        sql = "UPDATE `city` SET reason = %s WHERE `city_name` = %s"
        cursor.execute(sql, (args['reason'], args["city_name"]))
        db.commit()
        
        return jsonify(status = "success", result = {"reason": args["reason"], "city_name": args["city_name"]})
    
    
    def delete(self):
        args = parser.parse_args()
        sql = "DELETE FROM `city` WHERE `city_name` = %s"
        cursor.execute(sql, (args["city_name"], ))
        db.commit()
        
        return jsonify(status = "success", result = {"city_name": args["city_name"]})
        # 실행된 후 프론트에서 get으로 redirect -> 삭제한 나라의 날씨 보이지 않음

api.add_resource(Weather, '/')

if __name__ == "__main__":
    app.run(port = 5000, debug = True, host = '0.0.0.0')
