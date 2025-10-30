from celery import Celery
from anthropic import Anthropic
from app.config import settings
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery_app = Celery(
    "tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task(bind=True, name='app.tasks.process_llm_request')
def process_llm_request(self, prompt: str):
    """
    Background task that processes LLM requests using Claude API
    """
    try:
        logger.info(f"Processing task {self.request.id}")
        
        client = Anthropic(api_key=settings.anthropic_api_key)
        
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        result = message.content[0].text
        
        processed_result = {
            "response": result.strip(),
            "model": "claude-sonnet-4-5-20250929",
            "prompt": prompt,
            "prompt_length": len(prompt),
            "response_length": len(result),
            "timestamp": time.time(),
            "task_id": self.request.id
        }
        
        logger.info(f"Task {self.request.id} completed successfully")
        return processed_result
        
    except Exception as e:
        logger.error(f"Task {self.request.id} failed: {str(e)}")
        raise Exception(f"{type(e).__name__}: {str(e)}")