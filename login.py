from flask import Blueprint, json, request, redirect, render_template, jsonify, make_response, session
from flask.helpers import url_for
import requests
from flask_jwt_extended import *
import pymysql

# DB 및 Collection 연결
db = pymysql.connect(
        user = 'root',
        host = '127.0.0.1',
        port = 3306,
        db = 'weather',
        charset = 'utf8'
    )
cursor = db.cursor()

from config import REST_API_KEY

kakaoOauth = Blueprint("kakaoOauth", __name__)

@kakaoOauth.route("/")
def hello():
    return render_template('index.html')

@kakaoOauth.route("/login")
def login():
    client_id = REST_API_KEY
    redirect_uri = "http://172.30.1.23:5000/oauth"
    kakao_oauthurl = f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
    return redirect(kakao_oauthurl)

@kakaoOauth.route("/oauth") # 위 라우팅에서 redirect 됨
def callback():
    try:
        code = request.args.get("code")  # callback 뒤에 붙어오는 request token
        client_id = REST_API_KEY
        redirect_uri = "http://172.30.1.23:5000/oauth"

        #Python에서 HTTP 요청을 보내는 모듈인 requests
        token_request = requests.get(
            f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={redirect_uri}&code={code}"
        )
        token_json = token_request.json()  # 위의 get 요청을 통해 받아온 데이터를 json화 해주면 이곳에 access token이 존재
        error = token_json.get("error",None)
        if error is not None :
            return make_response({"message": "INVALID_CODE"}, 400) # 에러 처리
        access_token = token_json.get("access_token") # 카카오 소셜로그인을 통해 유저에 대한 정보를 받을 권한이 있는 토큰
        # access token 받아오는 통신

        # access token 기반으로 유저 정보 요청하는 통신
        profile_request = requests.get(
                "https://kapi.kakao.com/v2/user/me", headers={"Authorization" : f"Bearer {access_token}"},
            )
        data = profile_request.json()
        kakao_id_number = data.get("id")
        username = data.get("properties").get("nickname")

        token = create_access_token(identity = kakao_id_number)

        # DB에 유저 정보가 있는지 확인
        sql = "SELECT id FROM `user` where id = %s"
        cursor.execute(sql, (kakao_id_number))
        user_id = cursor.fetchall()

        # 유저가 로그인한 이력이 있는 경우, 닉네임 변경시 갱신  
        if user_id:
            sql = "UPDATE `user` SET username = %s WHERE `id` = %s"
            cursor.execute(sql, (username, kakao_id_number))
            db.commit()
            return jsonify(status = 200, token = token, user = True)
            # return redirect('http://172.30.1.23:5000/weather')

        # 유저가 로그인한 이력이 없는 경우 DB에 유저 정보 저장
        else:
            sql = "INSERT INTO `user` (`id`, `username`) VALUES (%s, %s)"
            cursor.execute(sql, (kakao_id_number, username))
            db.commit() #처음 로그인
            return redirect('http://172.30.1.23:5000/weather')

    except KeyError:
        return make_response({"message" : "INVALID_TOKEN"}, 400)

    except access_token.DoesNotExist:
        return make_response({"message" : "INVALID_TOKEN"}, 400)

@kakaoOauth.route("/protected")
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    print("cu",current_user)
    if current_user:
        return jsonify(
            status = 200,
            logged_in_as = current_user
        )
    else:
        return jsonify(
            status = 400,
            error = "access_token is expired"
        )
