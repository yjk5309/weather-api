from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import JWT_SECRET_KEY


app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours = 1)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days = 30)
jwt = JWTManager(app)

from login import kakaoOauth
app.register_blueprint(kakaoOauth)

from weather import weather
app.register_blueprint(weather)

if __name__ == "__main__":
    app.run(port = 5000, debug = True, host = '0.0.0.0')
