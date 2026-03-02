# tasks.py
from celery import shared_task
from .WhatsApp import collect_messages_from_all_chats


@shared_task
def collect_user_messages(user_id):
    collect_messages_from_all_chats(user_id)


from celery import shared_task

@shared_task
def add(x, y):
    return x + y