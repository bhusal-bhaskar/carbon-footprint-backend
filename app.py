from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta
from routes.auth_routes import auth_bp, init_auth_routes
from routes.activity_routes import activity_bp, init_activity_routes
from routes.analytics_routes import analytics_bp, init_analytics_routes  
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/carbonDB"
app.config["JWT_SECRET_KEY"] = "supersecretkey123"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)

mongo = PyMongo(app)
jwt = JWTManager(app)
CORS(app)

init_auth_routes(mongo)
init_activity_routes(mongo)
init_analytics_routes(mongo)  

app.register_blueprint(auth_bp)
app.register_blueprint(activity_bp)
app.register_blueprint(analytics_bp)  

if __name__ == "__main__":
    app.run(debug=True, port=5001)