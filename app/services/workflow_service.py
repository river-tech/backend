from typing import List, Optional
from app.models.workflow import Workflow
from app.db.database import SessionLocal

class WorkflowService:
    @staticmethod
    def get_all_workflows() -> List[Workflow]:
        db = SessionLocal()
        try:
            return db.query(Workflow).all()
        finally:
            db.close()
    
    @staticmethod
    def get_workflow_by_id(workflow_id: str) -> Optional[Workflow]:
        db = SessionLocal()
        try:
            return db.query(Workflow).filter(Workflow.id == workflow_id).first()
        finally:
            db.close()
