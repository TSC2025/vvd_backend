# project_tools.py
# In agentic-system/tools/project_tools.py

from typing import Dict, Any, Optional
from services.firestore_service import firestore_db
from collections import defaultdict

def get_data_by_village(village_name: Optional[str] = None) -> Dict[str, Any]:
    """
    For Admins. Gets a summary of projects and activities for a specific village, or for all villages.
    If 'village_name' is provided, it returns a list of projects and activities for that village.
    If 'village_name' is omitted, it returns a summary grouped by each village found.
    This tool assumes that 'Village' is a field name in the dynamic data of projects and activities.
    
    Args:
        village_name (Optional[str]): The name of the village to look up.

    Returns:
        A dictionary containing project and activity data related to the village(s).
    """
    print(f"Executing get_data_by_village for village_name: '{village_name}'")
    try:
        if village_name:
            # --- Case 1: Get data for a specific village ---
            print(f"Querying for specific village: {village_name}")
            projects_query = firestore_db.collection('VVDProjects').where("Village", "==", village_name).stream()
            activities_query = firestore_db.collection('VVDActivity').where("Village", "==", village_name).stream()
            
            project_list = [p.to_dict().get("Project Name", "Unnamed Project") for p in projects_query]
            activity_list = [a.to_dict().get("subFormName", "Unnamed Activity") for a in activities_query]
            
            if not project_list and not activity_list:
                return {"status": "success", "message": f"No projects or activities found for village '{village_name}'."}

            return {
                "status": "success",
                "village_name": village_name,
                "projects": project_list,
                "activities": activity_list
            }
        else:
            # --- Case 2: Get a summary for all villages ---
            print("Querying for all village data summary...")
            village_summary = defaultdict(lambda: {"projects": [], "activities": []})

            all_projects = firestore_db.collection('VVDProjects').stream()
            for doc in all_projects:
                data = doc.to_dict()
                # Your forms might save a single village or a list of them
                villages = data.get("Village") or data.get("Villages", [])
                if not isinstance(villages, list):
                    villages = [villages] # Handle single string case
                
                for v_name in villages:
                    if v_name:
                        project_name = data.get("Project Name", "Unnamed Project")
                        village_summary[v_name]["projects"].append(project_name)

            all_activities = firestore_db.collection('VVDActivity').stream()
            for doc in all_activities:
                data = doc.to_dict()
                villages = data.get("Village") or data.get("Villages", [])
                if not isinstance(villages, list):
                    villages = [villages]
                
                for v_name in villages:
                    if v_name:
                        activity_name = data.get("subFormName", "Unnamed Activity")
                        village_summary[v_name]["activities"].append(activity_name)
            
            if not village_summary:
                return {"status": "success", "message": "No village data found in any projects or activities."}

            return {"status": "success", "summary_by_village": dict(village_summary)}

    except Exception as e:
        print(f"An error occurred in get_data_by_village: {e}")
        return {"status": "error", "message": "An internal error occurred while fetching village data."}


def get_projects_by_beneficiary(beneficiary_name: str) -> Dict[str, Any]:
    """
    Finds all projects and activities associated with a specific beneficiary name.
    This tool assumes 'Beneficiary' or a similar key exists in the dynamic form data.

    Args:
        beneficiary_name (str): The name of the beneficiary to search for.

    Returns:
        A dictionary containing a list of related projects and activities.
    """
    print(f"Executing get_projects_by_beneficiary for: '{beneficiary_name}'")
    try:
        # Note: Firestore's "==" query on an array field checks if the value exists in the array.
        # This is powerful. We check for 'Beneficiary' (single) and 'Beneficiaries' (plural).
        projects_q1 = firestore_db.collection('VVDProjects').where("Beneficiary", "==", beneficiary_name).stream()
        projects_q2 = firestore_db.collection('VVDProjects').where("Beneficiaries", "array-contains", beneficiary_name).stream()
        
        activities_q1 = firestore_db.collection('VVDActivity').where("Beneficiary", "==", beneficiary_name).stream()
        activities_q2 = firestore_db.collection('VVDActivity').where("Beneficiaries", "array-contains", beneficiary_name).stream()
        
        # Combine results and remove duplicates
        project_names = {p.to_dict().get("Project Name", "Unnamed Project") for p in projects_q1}
        project_names.update({p.to_dict().get("Project Name", "Unnamed Project") for p in projects_q2})
        
        activity_names = {a.to_dict().get("subFormName", "Unnamed Activity") for a in activities_q1}
        activity_names.update({a.to_to_dict().get("subFormName", "Unnamed Activity") for a in activities_q2})

        if not project_names and not activity_names:
            return {"status": "success", "message": f"No projects or activities found for beneficiary '{beneficiary_name}'."}

        return {
            "status": "success",
            "beneficiary_name": beneficiary_name,
            "related_projects": list(project_names),
            "related_activities": list(activity_names),
        }
    except Exception as e:
        print(f"An error occurred in get_projects_by_beneficiary: {e}")
        return {"status": "error", "message": "An internal error occurred while fetching beneficiary data."}