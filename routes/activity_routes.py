from flask import Blueprint, request, jsonify

from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from utils.validators import validate_activity_data
from utils.emission_calculator import calculate_carbon_footprint
import uuid
from datetime import datetime

activity_bp = Blueprint('activities', __name__)
mongo = None

def init_activity_routes(mongo_instance):
    global mongo
    mongo = mongo_instance


# ─── CREATE ────────────────────────────────────────────────────────────────────
@activity_bp.route('/activities', methods=['POST'])
@jwt_required()
def create_activity():
    data = request.get_json()
    current_user = get_jwt_identity()

    errors = validate_activity_data(data)
    if errors:
        return jsonify({"errors": errors}), 400

    calculated_emission = calculate_carbon_footprint(
        data['activity_value'],
        data['emission_factor']
    )

    new_activity = {
        "_id": "ACT-" + str(uuid.uuid4())[:8].upper(),
        "user_id": current_user,
        "activity_type": data['activity_type'],
        "activity_detail": data.get('activity_detail', ''),
        "activity_value": data['activity_value'],
        "emission_factor": data['emission_factor'],
        "carbon_emission": calculated_emission,
        "unit": data['unit'],
        "timestamp": data.get('timestamp', datetime.utcnow().strftime('%Y-%m-%d')),
        "sources": []
    }

    mongo.db.activities.insert_one(new_activity)
    activity_id = new_activity['_id']
    new_activity.pop('_id')
    return jsonify({"message": "Activity logged successfully", "data": new_activity, "_id": activity_id}), 201


# ─── GET ALL ───────────────────────────────────────────────────────────────────
@activity_bp.route('/activities', methods=['GET'])
@jwt_required()
def get_activities():
    current_user = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')

    # Admin sees all, user sees only their own
    if role == 'admin':
        activities = list(mongo.db.activities.find({}, {"_id": 0}))
    else:
        activities = list(mongo.db.activities.find(
            {"user_id": current_user},
            {"_id": 0}
        ))

    return jsonify({"data": activities, "total": len(activities)}), 200


# ─── GET ONE ───────────────────────────────────────────────────────────────────
@activity_bp.route('/activities/<activity_id>', methods=['GET'])
@jwt_required()
def get_activity(activity_id):
    current_user = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')

    activity = mongo.db.activities.find_one(
        {"_id": activity_id},
        {"_id": 0}
    )

    if not activity:
        return jsonify({"error": "Activity not found"}), 404

    # User can only see their own activity
    if role != 'admin' and activity['user_id'] != current_user:
        return jsonify({"error": "Unauthorised"}), 403

    return jsonify({"data": activity}), 200


# ─── UPDATE ────────────────────────────────────────────────────────────────────
@activity_bp.route('/activities/<activity_id>', methods=['PUT'])
@jwt_required()
def update_activity(activity_id):
    data = request.get_json()
    current_user = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')

    activity = mongo.db.activities.find_one({"_id": activity_id})
    if not activity:
        return jsonify({"error": "Activity not found"}), 404

    if role != 'admin' and activity['user_id'] != current_user:
        return jsonify({"error": "Unauthorised"}), 403

    new_value = data.get('activity_value', activity['activity_value'])
    new_factor = data.get('emission_factor', activity['emission_factor'])
    data['carbon_emission'] = calculate_carbon_footprint(new_value, new_factor)

    data.pop('_id', None)
    data.pop('user_id', None)

    mongo.db.activities.update_one(
        {"_id": activity_id},
        {"$set": data}
    )

    return jsonify({"message": "Activity updated successfully"}), 200


# ─── DELETE ────────────────────────────────────────────────────────────────────
@activity_bp.route('/activities/<activity_id>', methods=['DELETE'])
@jwt_required()
def delete_activity(activity_id):
    current_user = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')

    activity = mongo.db.activities.find_one({"_id": activity_id})
    if not activity:
        return jsonify({"error": "Activity not found"}), 404

    if role != 'admin' and activity['user_id'] != current_user:
        return jsonify({"error": "Unauthorised"}), 403

    mongo.db.activities.delete_one({"_id": activity_id})
    return jsonify({"message": "Activity deleted successfully"}), 200


# ─── ADD SOURCE ────────────────────────────────────────────────────────────────
@activity_bp.route('/activities/<activity_id>/sources', methods=['POST'])
@jwt_required()
def add_source(activity_id):
    data = request.get_json()

    activity = mongo.db.activities.find_one({"_id": activity_id})
    if not activity:
        return jsonify({"error": "Activity not found"}), 404

    new_source = {
        "source_id": "SRC-" + str(uuid.uuid4())[:6].upper(),
        "description": data.get('description', ''),
        "distance_km": data.get('distance_km', 0),
        "emission_kg": data.get('emission_kg', 0)
    }

    mongo.db.activities.update_one(
        {"_id": activity_id},
        {"$push": {"sources": new_source}}
    )

    return jsonify({"message": "Source added successfully", "source": new_source}), 201


# ─── UPDATE SOURCE ─────────────────────────────────────────────────────────────
@activity_bp.route('/activities/<activity_id>/sources/<source_id>', methods=['PUT'])
@jwt_required()
def update_source(activity_id, source_id):
    data = request.get_json()

    activity = mongo.db.activities.find_one({"_id": activity_id})
    if not activity:
        return jsonify({"error": "Activity not found"}), 404

    source = next((s for s in activity['sources'] if s['source_id'] == source_id), None)
    if not source:
        return jsonify({"error": "Source not found"}), 404

    update_fields = {}
    if 'description' in data:
        update_fields["sources.$.description"] = data['description']
    if 'distance_km' in data:
        update_fields["sources.$.distance_km"] = data['distance_km']
    if 'emission_kg' in data:
        update_fields["sources.$.emission_kg"] = data['emission_kg']

    mongo.db.activities.update_one(
        {"_id": activity_id, "sources.source_id": source_id},
        {"$set": update_fields}
    )

    return jsonify({"message": "Source updated successfully"}), 200


# ─── DELETE SOURCE ─────────────────────────────────────────────────────────────
@activity_bp.route('/activities/<activity_id>/sources/<source_id>', methods=['DELETE'])
@jwt_required()
def delete_source(activity_id, source_id):
    activity = mongo.db.activities.find_one({"_id": activity_id})
    if not activity:
        return jsonify({"error": "Activity not found"}), 404

    source = next((s for s in activity['sources'] if s['source_id'] == source_id), None)
    if not source:
        return jsonify({"error": "Source not found"}), 404

    mongo.db.activities.update_one(
        {"_id": activity_id},
        {"$pull": {"sources": {"source_id": source_id}}}
    )

    return jsonify({"message": "Source deleted successfully"}), 200


# ─── FILTER BY ACTIVITY TYPE ───────────────────────────────────────────────────
@activity_bp.route('/activities/filter/type', methods=['GET'])
@jwt_required()
def filter_by_type():
    current_user = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')
    activity_type = request.args.get('activity_type')

    if not activity_type:
        return jsonify({"error": "activity_type parameter is required"}), 400

    if role == 'admin':
        activities = list(mongo.db.activities.find(
            {"activity_type": activity_type},
            {"_id": 0}
        ))
    else:
        activities = list(mongo.db.activities.find(
            {"user_id": current_user, "activity_type": activity_type},
            {"_id": 0}
        ))

    return jsonify({"data": activities, "total": len(activities)}), 200


# ─── FILTER BY DATE RANGE ──────────────────────────────────────────────────────
@activity_bp.route('/activities/filter/date', methods=['GET'])
@jwt_required()
def filter_by_date():
    current_user = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not start_date or not end_date:
        return jsonify({"error": "start_date and end_date are required"}), 400

    if role == 'admin':
        activities = list(mongo.db.activities.find(
            {"timestamp": {"$gte": start_date, "$lte": end_date}},
            {"_id": 0}
        ))
    else:
        activities = list(mongo.db.activities.find(
            {"user_id": current_user, "timestamp": {"$gte": start_date, "$lte": end_date}},
            {"_id": 0}
        ))

    return jsonify({"data": activities, "total": len(activities)}), 200


# ─── FILTER BY MIN EMISSION ────────────────────────────────────────────────────
@activity_bp.route('/activities/filter/emission', methods=['GET'])
@jwt_required()
def filter_by_emission():
    current_user = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')
    min_emission = request.args.get('min_emission')

    if not min_emission:
        return jsonify({"error": "min_emission parameter is required"}), 400

    if role == 'admin':
        activities = list(mongo.db.activities.find(
            {"carbon_emission": {"$gte": float(min_emission)}},
            {"_id": 0}
        ))
    else:
        activities = list(mongo.db.activities.find(
            {"user_id": current_user, "carbon_emission": {"$gte": float(min_emission)}},
            {"_id": 0}
        ))

    return jsonify({"data": activities, "total": len(activities)}), 200


# ─── TOP EMITTING ──────────────────────────────────────────────────────────────
@activity_bp.route('/activities/top-emitting', methods=['GET'])
@jwt_required()
def top_emitting():
    current_user = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')

    if role == 'admin':
        activities = list(mongo.db.activities.find(
            {}, {"_id": 0}
        ).sort("carbon_emission", -1))
    else:
        activities = list(mongo.db.activities.find(
            {"user_id": current_user},
            {"_id": 0}
        ).sort("carbon_emission", -1))

    return jsonify({"data": activities, "total": len(activities)}), 200