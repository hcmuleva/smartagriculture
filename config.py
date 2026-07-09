"""
All settings and configuration in one place.
Change the DATABASE_URL to match your local PostgreSQL setup.
Format: postgresql://username:password@localhost:5432/database_name
"""
 
class Config:
    # Change 'nitin' and 'password' to your actual PostgreSQL username and password
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:nitin123@localhost:5432/smartagriculture"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = "uploads"
 