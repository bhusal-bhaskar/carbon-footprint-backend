from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

analytics_bp = Blueprint('analytics', __name__)
mongo = None

def init_analytics_routes(mongo_instance):
    global mongo
    mongo = mongo_instance


# ─── TOTAL EMISSIONS PER USER ──────────────────────────────────────────────────
@analytics_bp.route('/analytics/total-emissions', methods=['GET'])
@jwt_required()
def total_emissions():
    current_user = get_jwt_identity()

    pipeline = [
        {"$match": {"user_id": current_user}},
        {"$group": {
            "_id": "$user_id",
            "total_emission_kg": {"$sum": "$carbon_emission"},
            "total_activities": {"$sum": 1}
        }}
    ]

    result = list(mongo.db.activities.aggregate(pipeline))
    return jsonify({"data": result}), 200


# ─── EMISSIONS BY TYPE ─────────────────────────────────────────────────────────
@analytics_bp.route('/analytics/emissions-by-type', methods=['GET'])
@jwt_required()
def emissions_by_type():
    current_user = get_jwt_identity()

    pipeline = [
        {"$match": {"user_id": current_user}},
        {"$group": {
            "_id": "$activity_type",
            "total_emission_kg": {"$sum": "$carbon_emission"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"total_emission_kg": -1}}
    ]

    result = list(mongo.db.activities.aggregate(pipeline))
    return jsonify({"data": result}), 200


# ─── MONTHLY TRENDS ────────────────────────────────────────────────────────────
@analytics_bp.route('/analytics/monthly-trends', methods=['GET'])
@jwt_required()
def monthly_trends():
    current_user = get_jwt_identity()

    pipeline = [
        {"$match": {"user_id": current_user}},
        {"$group": {
            "_id": {
                "year": {"$substr": ["$timestamp", 0, 4]},
                "month": {"$substr": ["$timestamp", 5, 2]}
            },
            "total_emission_kg": {"$sum": "$carbon_emission"},
            "activity_count": {"$sum": 1}
        }},
        {"$sort": {"_id.year": 1, "_id.month": 1}}
    ]

    result = list(mongo.db.activities.aggregate(pipeline))
    return jsonify({"data": result}), 200


# ─── HIGHEST ACTIVITIES ────────────────────────────────────────────────────────
@analytics_bp.route('/analytics/highest-activities', methods=['GET'])
@jwt_required()
def highest_activities():
    current_user = get_jwt_identity()

    pipeline = [
        {"$match": {"user_id": current_user}},
        {"$group": {
            "_id": "$activity_type",
            "total_emission_kg": {"$sum": "$carbon_emission"},
            "avg_emission_kg": {"$avg": "$carbon_emission"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"total_emission_kg": -1}}
    ]

    result = list(mongo.db.activities.aggregate(pipeline))
    return jsonify({"data": result}), 200