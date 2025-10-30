
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from app.tasks import process_llm_request, celery_app
from typing import Optional, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Assistant Task Processor",
    description="Asynchronous LLM task processing API using Claude AI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Explain asynchronous processing in simple terms"
            }
        }

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.get("/")
def root():
    return {
        "message": "AI Assistant Task Processor API",
        "version": "1.0.0",
        "endpoints": {
            "POST /submit": "Submit a new task",
            "GET /status/{task_id}": "Check task status",
            "DELETE /cancel/{task_id}": "Cancel a task",
            "GET /tasks/recent": "List recent tasks",
            "GET /health": "Health check",
            "GET /docs": "API documentation"
        }
    }

@app.post("/submit", response_model=TaskResponse)
def submit_task(request: TaskRequest):
    try:
        logger.info("Submitting new task")
        task = process_llm_request.delay(request.prompt)
        
        return TaskResponse(
            task_id=task.id,
            status="PENDING",
            message="Task submitted successfully"
        )
    except Exception as e:
        logger.error(f"Failed to submit task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str):
    try:
        task = celery_app.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            return TaskStatusResponse(task_id=task_id, status="PENDING")
        elif task.state == 'STARTED':
            return TaskStatusResponse(task_id=task_id, status="PROCESSING")
        elif task.state == 'SUCCESS':
            return TaskStatusResponse(task_id=task_id, status="SUCCESS", result=task.result)
        elif task.state == 'FAILURE':
            return TaskStatusResponse(task_id=task_id, status="FAILURE", error=str(task.info))
        else:
            return TaskStatusResponse(task_id=task_id, status=task.state, result=task.info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "AI Assistant Task Processor"}

@app.delete("/cancel/{task_id}")
def cancel_task(task_id: str):
    try:
        celery_app.control.revoke(task_id, terminate=True, signal='SIGKILL')
        return {"message": f"Task {task_id} cancellation requested"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/recent")
def list_recent_tasks():
    try:
        inspector = celery_app.control.inspect()
        return {
            "active_tasks": inspector.active() or {},
            "scheduled_tasks": inspector.scheduled() or {},
            "reserved_tasks": inspector.reserved() or {}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))