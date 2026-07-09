from flask import Flask
from config import Config
from models import db, Disease
from routes.scans import scans_bp
from routes.tasks import tasks_bp
from services.ai_service import load_model

def seed_diseases(app):
    """Pre-fill disease table on first run so it is never empty."""
    with app.app_context():
        if Disease.query.count() == 0:
            diseases = [
                Disease(
                    disease_name="healthy",
                    pesticide_name=None,
                    dosage="N/A",
                    spray_interval_days=None,
                    description="Plant is healthy. No action needed."
                ),
                Disease(
                    disease_name="early_blight",
                    pesticide_name="Chlorothalonil",
                    dosage="2 g/L",
                    spray_interval_days=7,
                    description="Fungal disease causing dark spots with yellow rings."
                ),
                Disease(
                    disease_name="late_blight",
                    pesticide_name="Mancozeb",
                    dosage="2 g/L",
                    spray_interval_days=5,
                    description="Water mould causing dark lesions on leaves and stems."
                ),
                Disease(
                    disease_name="leaf_mold",
                    pesticide_name="Chlorothalonil",
                    dosage="2 g/L",
                    spray_interval_days=7,
                    description="Fungal disease causing yellow spots on the upper leaf surface and olive-green mold on the underside of leaves."
                ),
                Disease(
                    disease_name="mosaic_virus",
                    pesticide_name=None,
                    dosage="N/A",
                    spray_interval_days=None,
                    description="Viral disease. No chemical cure - remove plant immediately."
                )
            ]
            db.session.add_all(diseases)
            db.session.commit()
            print("Diseases seeded successfully.")
        else:
            print("Disease table already seeded.")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(scans_bp)
    app.register_blueprint(tasks_bp)

    with app.app_context():
        db.create_all()
        print("Database tables created.")

    seed_diseases(app)
    load_model()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
