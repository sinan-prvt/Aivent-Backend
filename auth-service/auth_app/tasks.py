from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging
from .rabbit import publish_event
import requests

logger = logging.getLogger(__name__)


@shared_task 
def sync_user_to_user_service_task(user_data): 
    url = settings.USER_SERVICE_URL.rstrip("/") + "/api/internal/users/" 
    token = settings.USER_SERVICE_INTERNAL_TOKEN 
    
    try: 
        resp = requests.post( 
            url, 
            json=user_data, 
            headers={"Authorization": f"Bearer {token}"}, 
            timeout=5 
        ) 
        return {"status": resp.status_code, "response": resp.text} 
    except Exception as e: 
        return {"status": "error", "message": str(e)}



@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, subject, message, recipient_list, from_email=None):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        return {"status": "sent"}
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3)
def publish_event_task(self, routing_key, payload):
    try:
        publish_event(routing_key, payload)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)