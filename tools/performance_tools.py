# In agentic-system/tools/performance_tools.py

from typing import Dict, Any, List, Optional
from services.firestore_service import firestore_db
from collections import defaultdict

# --- Tool for the Staff Agent ---

def get_my_performance(user_id: str) -> Dict[str, Any]:
    """
    Gets a performance summary for the currently logged-in user.
    It finds all projects and activities where the 'Assigned to' field matches the user's name.
    The user_id is provided automatically by the system from the authenticated user.
    
    Args:
        user_id (str): The UID of the authenticated user.

    Returns:
        A dictionary containing a summary of the user's assigned projects and activities.
    """
    print(f"Executing get_my_performance for user_id: {user_id}")
    try:
        # Step 1: Get the user's display name from the 'Users' collection.
        user_doc = firestore_db.collection('Users').document(user_id).get()
        if not user_doc.exists:
            return {"status": "error", "message": "Could not find your user profile in the database."}
        
        user_display_name = user_doc.to_dict().get('displayName')
        if not user_display_name:
            return {"status": "error", "message": "Your user profile does not have a display name set."}
        
        print(f"User's name is '{user_display_name}'. Querying collections...")

        # Step 2: Query VVDProjects and VVDActivity for this user.
        # This syntax is how you query a field name that contains spaces.
        projects_query = firestore_db.collection('VVDProjects').where("Assigned to", "==", user_display_name).stream()
        activities_query = firestore_db.collection('VVDActivity').where("Assigned to", "==", user_display_name).stream()
        
        project_list = [p.to_dict().get("Project Name", "Unnamed Project") for p in projects_query]
        activity_list = [a.to_dict().get("subFormName", "Unnamed Activity") for a in activities_query]
        
        if not project_list and not activity_list:
            return {"status": "success", "message": f"No projects or activities are currently assigned to you ({user_display_name})."}

        return {
            "status": "success",
            "summary": f"Found {len(project_list)} projects and {len(activity_list)} activities assigned to {user_display_name}.",
            "assigned_projects": project_list,
            "assigned_activities": activity_list
        }

    except Exception as e:
        print(f"An error occurred in get_my_performance: {e}")
        return {"status": "error", "message": f"An internal error occurred while fetching your performance data."}


# --- Tool for the Admin Agent ---

def get_staff_performance(staff_name: Optional[str] = None) -> Dict[str, Any]:
    """
    For Admins. Gets a performance summary for a specific staff member or all staff members.
    If 'staff_name' is provided, it returns assignments for that person.
    If 'staff_name' is omitted, it returns a summary grouped by each staff member found.

    Args:
        staff_name (Optional[str]): The full name of the staff member to look up.

    Returns:
        A dictionary containing performance data.
    """
    print(f"Executing get_staff_performance for staff_name: '{staff_name}'")
    try:
        if staff_name:
            # --- Case 1: Get performance for a specific staff member ---
            print(f"Querying for specific staff: {staff_name}")
            projects_query = firestore_db.collection('VVDProjects').where("Assigned to", "==", staff_name).stream()
            activities_query = firestore_db.collection('VVDActivity').where("Assigned to", "==", staff_name).stream()
            
            project_list = [p.to_dict().get("Project Name", "Unnamed Project") for p in projects_query]
            activity_list = [a.to_dict().get("subFormName", "Unnamed Activity") for a in activities_query]
            
            if not project_list and not activity_list:
                return {"status": "success", "message": f"No projects or activities found assigned to {staff_name}."}

            return {
                "status": "success",
                "staff_name": staff_name,
                "assigned_projects": project_list,
                "assigned_activities": activity_list
            }
        else:
            # --- Case 2: Get a summary for all staff members ---
            print("Querying for all staff performance summary...")
            # defaultdict simplifies adding to lists for new keys
            performance_summary = defaultdict(lambda: {"projects": [], "activities": []})

            all_projects = firestore_db.collection('VVDProjects').stream()
            for doc in all_projects:
                data = doc.to_dict()
                assigned_to = data.get("Assigned to")
                if assigned_to:
                    project_name = data.get("Project Name", "Unnamed Project")
                    performance_summary[assigned_to]["projects"].append(project_name)

            all_activities = firestore_db.collection('VVDActivity').stream()
            for doc in all_activities:
                data = doc.to_dict()
                assigned_to = data.get("Assigned to")
                if assigned_to:
                    activity_name = data.get("subFormName", "Unnamed Activity")
                    performance_summary[assigned_to]["activities"].append(activity_name)
            
            if not performance_summary:
                return {"status": "success", "message": "No assignments found for any staff member."}

            # Convert defaultdict to a regular dict for the final response
            return {"status": "success", "summary_by_staff": dict(performance_summary)}

    except Exception as e:
        print(f"An error occurred in get_staff_performance: {e}")
        return {"status": "error", "message": "An internal error occurred while fetching staff performance."}