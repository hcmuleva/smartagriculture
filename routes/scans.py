from flask import Blueprint, request, jsonify
from models import db, Plant, Scan, Diagnosis, Disease, TreatmentTask
from services.ai_service import predict_disease
from datetime import datetime
import os

scans_bp = Blueprint("scans", __name__)


@scans_bp.route("/api/v1/scans", methods=["POST"])
def receive_scan():

    # --- Step 1: Validate incoming data ---
    if "image" not in request.files:
        return jsonify({"error": "No image sent. Use key 'image'."}), 400
    
    if "latitude" not in request.form:
        return jsonify({"error": "No latitude sent. Use key 'latitude'."}), 400
    
    if "longitude" not in request.form:
        return jsonify({"error": "No longitude sent. Use key 'longitude'."}), 400
    
    if "timestamp" not in request.form:
        return jsonify({"error": "No timestamp sent. Use key 'timestamp'."}), 400

    image_file = request.files["image"]
    latitude  = float(request.form["latitude"])
    longitude = float(request.form["longitude"])
    timestamp = request.form["timestamp"]

    # --- Step 2: Save image to disk ---
    filename   = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{image_file.filename}"
    image_path = os.path.join("uploads", filename)
    image_file.save(image_path)

    # --- Step 3: Save or find the crop record ---
    plant = Plant.query.filter_by(
        latitude=latitude,
        longitude=longitude
    ).first()
    if not plant:
        plant = Plant(
            latitude=latitude,
            longitude=longitude
        )
        db.session.add(plant)
        db.session.flush()

    # --- Step 4: Save the scan record ---
    scan = Scan(
        plant_id=plant.id,
        image_path=image_path,
        timestamp=datetime.fromisoformat(timestamp),
    )
    db.session.add(scan)
    db.session.flush()

    # --- Step 5: Run AI model ---
    result = predict_disease(image_path)
    disease_name = result["disease"]
    confidence = result["confidence"]

    # --- Step 6: Search disease table for pesticide and spray interval ---
    disease = Disease.query.filter_by(disease_name=disease_name).first()
    if not disease:
        return jsonify({"error": f"Unknown disease returned by model: {disease_name}"}), 400

    # --- Step 7: Save diagnosis ---
    diagnosis = Diagnosis(
        scan_id = scan.id,
        disease_id = disease.id,
        confidence = confidence,
    )
    db.session.add(diagnosis)
    db.session.flush()

    # --- Step 8: Create task only if plant is diseased (not healthy) ---
    task = None
    if disease.pesticide_name:
        task = TreatmentTask(
            diagnosis_id   = diagnosis.id,
            plant_id       = plant.id,
            status         = "pending",
        )
        db.session.add(task)

    db.session.commit()

    # --- Step 9: Respond to robot ---
    return jsonify({
        "scan_id": scan.id,
        "plant_id": plant.id,
        "disease": disease.disease_name,
        "confidence": confidence,
        "pesticide": disease.pesticide_name,
        "dosage": disease.dosage,
        "spray_interval_days": disease.spray_interval_days,
        "task_created": task is not None,
        "status": "task_created" if task else "no_action_needed",
    }), 201


@scans_bp.route("/api/v1/scans", methods=["GET"])
def get_scans():
    """Dashboard - see all scans with their diagnosis."""
    scans = Scan.query.order_by(Scan.created_at.desc()).all()
    return jsonify([
        {
            "scan_id": s.id,
            "plant_id": s.plant_id,
            "latitude": s.plant.latitude,
            "longitude": s.plant.longitude,
            "timestamp": s.timestamp.isoformat(),
            "disease": s.diagnosis.disease.disease_name if s.diagnosis else None,
            "pesticide": s.diagnosis.disease.pesticide_name if s.diagnosis else None,
            "dosage": s.diagnosis.disease.dosage if s.diagnosis else None,
            "spray_interval_days": s.diagnosis.disease.spray_interval_days if s.diagnosis else None,
            "confidence": s.diagnosis.confidence if s.diagnosis else None,
        }
        for s in scans
    ])

