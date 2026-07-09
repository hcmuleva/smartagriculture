from flask import Blueprint, request, jsonify
from models import db, TreatmentTask
from datetime import datetime

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/api/v1/tasks/pending", methods=["GET"])
def get_pending_tasks():
    """Robot calls this to get its next spray jobs."""
    tasks = TreatmentTask.query.filter_by(status="pending").all()
    return jsonify([
        {
            "task_id": t.id,
            "plant_id": t.plant_id,
            "latitude": t.plant.latitude,
            "longitude": t.plant.longitude,
            "disease": t.diagnosis.disease.disease_name,
            "confidence": t.diagnosis.confidence,
            "pesticide": t.diagnosis.disease.pesticide_name,
            "dosage": t.diagnosis.disease.dosage,
            "spray_interval_days": t.diagnosis.disease.spray_interval_days,
            "status": t.status,
        }
        for t in tasks
    ])


@tasks_bp.route("/api/v1/tasks/<int:task_id>/complete", methods=["PATCH"])
def complete_task(task_id):
    """Robot calls this after it has applied the pesticide."""
    task = TreatmentTask.query.get_or_404(task_id)
    task.status = "completed"
    task.completed_at = datetime.utcnow()
    db.session.commit()
    return jsonify({
        "task_id": task.id,
        "status":  "completed",
        "message": "Task marked as completed successfully."
    })


@tasks_bp.route("/api/v1/tasks", methods=["GET"])
def get_all_tasks():
    """Dashboard - see all tasks and their status."""
    tasks = TreatmentTask.query.order_by(TreatmentTask.created_at.desc()).all()
    return jsonify([
        {
            "task_id": t.id,
            "plant_id": t.plant_id,
            "latitude": t.plant.latitude,
            "longitude": t.plant.longitude,
            "disease": t.diagnosis.disease.disease_name,
            "confidence": t.diagnosis.confidence,
            "pesticide": t.diagnosis.disease.pesticide_name,
            "dosage": t.diagnosis.disease.dosage,
            "spray_interval_days": t.diagnosis.disease.spray_interval_days,
            "status": t.status,
            "created_at": t.created_at.isoformat(),
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
        }
        for t in tasks
    ])

