# In agentic-system/services/firestore_service.py

import firebase_admin
from firebase_admin import credentials, firestore
import os

# This logic runs once when the module is first imported (e.g., in main.py)
if not firebase_admin._apps:
    try:
        # Recommended for production (e.g., Cloud Run, GKE) where the environment
        # is already authenticated. It automatically uses the service account.
        print("Attempting to initialize Firebase with Application Default Credentials...")
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {'projectId': os.getenv("GCP_PROJECT_ID")})
        print("Firebase Admin SDK initialized successfully (ADC).")
    except Exception:
        # Fallback for local development where GOOGLE_APPLICATION_CREDENTIALS is set explicitly.
        print("ADC failed. Attempting to initialize Firebase with explicit file path...")
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized successfully (File Path).")
        else:
            print("ERROR: Firebase Admin SDK could not be initialized. "
                  "Ensure GOOGLE_APPLICATION_CREDENTIALS is set and valid, "
                  "or your environment is configured for ADC.")
            raise

# Export the firestore database client for use in other services and tools
firestore_db = firestore.client()