"""
Firebase Configuration & Initialization
Handles Firestore client setup using a service account key.
"""
import os
import firebase_admin
from firebase_admin import credentials, firestore

# Path to your Firebase Service Account JSON key
# Download from: Firebase Console → Project Settings → Service Accounts → Generate New Private Key
SERVICE_ACCOUNT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "firebase_service_account.json"
)

# Firestore collection name for storing posts
POSTS_COLLECTION = "linkedin_posts"

_db = None  # Module-level singleton


def get_firestore_client():
    """
    Returns a Firestore client instance (singleton).
    Initializes the Firebase Admin SDK on first call.
    """
    global _db

    if _db is not None:
        return _db

    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        raise FileNotFoundError(
            f"🔴 Firebase service account key not found at:\n"
            f"   {SERVICE_ACCOUNT_PATH}\n\n"
            f"   To fix this:\n"
            f"   1. Go to Firebase Console → Project Settings → Service Accounts\n"
            f"   2. Click 'Generate new private key'\n"
            f"   3. Save the downloaded JSON file as 'firebase_service_account.json'\n"
            f"   4. Place it in the firebase_publishing/ folder"
        )

    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)

    # Only initialize the app if it hasn't been initialized yet
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    _db = firestore.client()
    print("✅ Firebase Firestore connected successfully.")
    return _db
