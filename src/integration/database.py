from sqlalchemy import create_engine, select, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

from ..functions.utils import assign_new_values

load_dotenv()

# Database connection
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_CONNECTION")

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    future=True,
    connect_args={"ssl": False}
)

SessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# Dependency to get DB session
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

from .models import WorkflowFormStructure, WorkflowStructure, WorkflowSubmission

async def get_all_workflows(db: AsyncSession):
    try:
        result = await db.execute(
            select(WorkflowStructure)
            .where(WorkflowStructure.is_deleted == False)
        )
        workflows = result.scalars().all()
        
        workflow_list = [
            {
                "id": workflow.id,
                "name": workflow.name,
                "description": workflow.description,
                "status": workflow.status,
                "fields": workflow.fields,
                "apiConfig": workflow.api_config,
                "category": workflow.category,
                "version": workflow.version,
                "isPublished": workflow.is_published,
                "createdAt": workflow.created_at.isoformat(),
                "updatedAt": workflow.updated_at.isoformat(),
                "createdBy": workflow.created_by
            }
            for workflow in workflows
        ]
        
        return workflow_list
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def get_workflow_by_id(db: AsyncSession, workflow_id: str):
    try:
        # Use async query instead of sync query
        result = await db.execute(
            select(WorkflowFormStructure)
            .where(WorkflowFormStructure.id == workflow_id)
        )
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            return {"status": "error", "message": f"Workflow with id {workflow_id} not found"}
            
        workflow_dict = {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "status": workflow.status,
            "fields": workflow.fields,
            "apiConfig": workflow.api_config,
            "isPublished": workflow.is_published,
        }
        
        return workflow_dict
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def update_workflow(db: AsyncSession, workflow_id: str, workflow_data: dict):
    try:
        # Use async query to find the workflow
        result = await db.execute(
            select(WorkflowStructure)
            .where(WorkflowStructure.id == workflow_id)
        )
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            return {"status": "error", "message": f"Workflow with id {workflow_id} not found"}

        # Assign new values using your utility function
        assign_new_values(workflow, workflow_data)
        
        # Use async methods to save changes
        db.add(workflow)
        await db.commit()
        
        return {
            "status": "success",
            "message": "Workflow updated successfully",
        }
    except Exception as e:
        await db.rollback()  # Use async rollback
        return {"status": "error", "message": str(e)}

async def create_workflow(db: AsyncSession, workflow_data: dict):
    try:
        # Create new WorkflowStructure instance
        new_workflow = WorkflowStructure(
            id=workflow_data.get('id'),
            name=workflow_data.get('name'),
            description=workflow_data.get('description'),
            status=workflow_data.get('status'),
            fields=workflow_data.get('fields'),
            api_config=workflow_data.get('apiConfig'),
            category=workflow_data.get('category'),
            version=workflow_data.get('version', 1),
            is_published=workflow_data.get('isPublished', False),
            created_by=workflow_data.get('createdBy')
        )
        
        # Add to database with async methods
        db.add(new_workflow)
        await db.commit()
        
        return {
            "status": "success",
            "message": "Workflow created successfully",
        }
        
    except Exception as e:
        await db.rollback()  # Use async rollback
        return {"status": "error", "message": str(e)}

async def delete_workflow(db: AsyncSession, workflow_id: str):
    try:
        # Find the workflow using async methods
        result = await db.execute(
            select(WorkflowStructure)
            .where(WorkflowStructure.id == workflow_id)
        )
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            return {"status": "error", "message": f"Workflow with id {workflow_id} not found"}
        
        # Set is_deleted to True
        workflow.is_deleted = True
        
        # Commit using async methods
        await db.commit()
        
        return {
            "status": "success",
            "message": "Workflow deleted successfully"
        }
        
    except Exception as e:
        await db.rollback()  # Use async rollback
        return {"status": "error", "message": str(e)}

async def create_workflow_submission(db: AsyncSession, submission_data: dict):
    try:
        # Create new WorkflowSubmission instance
        new_submission = WorkflowSubmission(
            workflow_id=submission_data.get('workflowId'),
            is_positive= True if submission_data.get('feedback') == "positive" else False
        )
        
        # Add to database with async methods
        db.add(new_submission)
        await db.commit()
        
        return {
            "status": "success",
            "message": "Workflow submission created successfully",
        }
        
    except Exception as e:
        await db.rollback()  # Use async rollback
        return {"status": "error", "message": str(e)}