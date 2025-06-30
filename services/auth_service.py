# In agentic-system/services/auth_service.py

from firebase_admin import auth
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Import our validated User model and the database client
from models.user_models import User
from .firestore_service import firestore_db

# This scheme tells FastAPI how to find the token in the request header
# It looks for "Authorization: Bearer <your_token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    FastAPI dependency that:
    1. Verifies the Firebase ID token from the request's Authorization header.
    2. Fetches the user's data from the Firestore 'Users' collection by querying their email.
    3. Validates the data against our Pydantic 'User' model.
    4. Returns the validated 'User' object, making it available to our API endpoints.
    """
    try:
        # Step 1: Verify the token using Firebase Admin SDK to get UID and email
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token.get('uid')
        email = decoded_token.get('email')
        
        if not uid or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is missing UID or email information."
            )

        # Step 2: Query the 'Users' collection by email, as per your logic
        user_query = firestore_db.collection("Users").where("email", "==", email).limit(1).stream()
        
        user_docs = list(user_query)
        if not user_docs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email {email} not found in our database."
            )

        # Step 3: Get the data and validate it with our Pydantic model
        user_data_from_db = user_docs[0].to_dict()
        
        # Add the uid and email from the token to the data before validation
        # This ensures our Pydantic model receives all the fields it expects.
        user_data_from_db['uid'] = uid
        user_data_from_db['email'] = email
        
        validated_user = User(**user_data_from_db)
        
        # Final check to ensure the roles list is not empty
        if not validated_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has an empty roles list and cannot be granted access."
            )
        
        return validated_user

    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )
    except Exception as e:
        # Catch other potential errors (like Pydantic validation errors or our own HTTPErrors)
        if isinstance(e, HTTPException):
            raise e # Re-raise if it's already a planned HTTP exception
        print(f"An unexpected error occurred during authentication: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred during authentication.",
        )