"""
Database tables defined as Python classes using SQLAlchemy.
Each class = one table in PostgreSQL.
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Plant(db.Model):
    """One row per plant the robot has ever scanned."""
    __tablename__ = "plants"

    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    # one crop can have many scans
    scans = db.relationship("Scan", backref="plant", lazy=True)

class Disease(db.Model):
    """Master table containing disease information and treatment details."""
    __tablename__ = "diseases"
    id = db.Column(db.Integer, primary_key=True)
    disease_name = db.Column(db.String(100), unique=True ,nullable=False)
    pesticide_name = db.Column(db.String(100), nullable=True)
    dosage = db.Column(db.String(50), nullable=False)
    spray_interval_days = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    diagnoses = db.relationship("Diagnosis", backref="disease", lazy=True)    

class Scan(db.Model):
    """One row per image the robot sends in."""
    __tablename__ = "scans"

    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey("plants.id"), nullable=False)
    image_path  = db.Column(db.String(255), nullable=False)
    timestamp   = db.Column(db.DateTime, nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)


    # one scan produces one diagnosis
    diagnosis = db.relationship("Diagnosis", backref="scan", uselist=False)


class Diagnosis(db.Model):
    """One row per disease result - what the AI model decided."""
    __tablename__ = "diagnoses"

    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey("scans.id"), nullable=False)
    disease_id = db.Column(db.Integer,db.ForeignKey("diseases.id"),nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # one diagnosis creates one task (if diseased)
    task = db.relationship("TreatmentTask", backref="diagnosis", uselist=False)


class TreatmentTask(db.Model):
    """One row per pesticide job the robot needs to do."""
    __tablename__ = "treatment_tasks"

    id = db.Column(db.Integer, primary_key=True)
    diagnosis_id = db.Column(db.Integer, db.ForeignKey("diagnoses.id"), nullable=False)
    plant_id = db.Column(db.Integer, db.ForeignKey("plants.id"), nullable=False)
    status = db.Column(db.String(20), default="pending", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    plant = db.relationship("Plant", backref="tasks")


