# budget_tools.py
# In agentic-system/tools/budget_tools.py

from typing import Dict, Any, Optional
from services.firestore_service import firestore_db
from models.project_models import VVDBudget, VVDRebate # Import our Pydantic models

def get_financial_report(project_name: Optional[str] = None) -> Dict[str, Any]:
    """
    For Accountants. Provides a financial report.
    If 'project_name' is given, it details the budget, rebates, and expenses for that specific project.
    If 'project_name' is omitted, it returns a high-level summary of all project budgets.
    
    Args:
        project_name (Optional[str]): The name of the project to get a detailed report for.

    Returns:
        A dictionary containing the financial report.
    """
    print(f"Executing get_financial_report for project_name: '{project_name}'")
    try:
        if project_name:
            # --- Case 1: Detailed report for a single project ---
            # First, find the project to get its ID.
            project_query = firestore_db.collection('VVDProjects').where("Project Name", "==", project_name).limit(1).stream()
            project_docs = list(project_query)
            if not project_docs:
                return {"status": "error", "message": f"Project '{project_name}' not found."}
            
            project_id = project_docs[0].id
            
            # Now fetch all financial documents related to this project_id
            project_budget_q = firestore_db.collection('vvdbudget').where("projectId", "==", project_id).where("activityId", "==", None).stream()
            activity_budgets_q = firestore_db.collection('vvdbudget').where("projectId", "==", project_id).stream()
            rebates_q = firestore_db.collection('vvdrebate').where("projectId", "==", project_id).stream()
            # Note: Reimbursements are linked to activities, so a more complex query/aggregation would be needed for a full expense report.
            # For now, we focus on budgets and rebates.
            
            # Process results
            project_budget_docs = list(project_budget_q)
            project_budget = VVDBudget(id=project_budget_docs[0].id, **project_budget_docs[0].to_dict()).dict() if project_budget_docs else None
            
            # Filter out the main project budget from the activity budgets list
            activity_budgets = [
                VVDBudget(id=doc.id, **doc.to_dict()).dict() for doc in activity_budgets_q if doc.to_dict().get('activityId')
            ]
            rebates = [VVDRebate(id=doc.id, **doc.to_dict()).dict() for doc in rebates_q]

            return {
                "status": "success",
                "project_name": project_name,
                "project_budget": project_budget,
                "activity_budgets": activity_budgets,
                "rebates": rebates
            }
        else:
            # --- Case 2: High-level summary of all project budgets ---
            all_budgets_q = firestore_db.collection('vvdbudget').where("activityId", "==", None).stream()
            
            budget_summary = []
            for doc in all_budgets_q:
                budget_data = doc.to_dict()
                # We need to find the project name from the projectId
                project_doc = firestore_db.collection('VVDProjects').document(budget_data.get('projectId')).get()
                p_name = project_doc.to_dict().get("Project Name", "Unknown Project") if project_doc.exists else "Unknown Project"
                
                budget_summary.append({
                    "project_name": p_name,
                    "budget_amount": budget_data.get("amount", 0)
                })
            
            if not budget_summary:
                return {"status": "success", "message": "No project-level budgets found."}

            return {"status": "success", "all_project_budgets": budget_summary}

    except Exception as e:
        print(f"An error occurred in get_financial_report: {e}")
        return {"status": "error", "message": "An internal error occurred while fetching the financial report."}