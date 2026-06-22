"""
Scheduler that periodically checks for tasks with remind_at <= now and not reminded,
then sends push notifications to stored subscriptions for the task owner.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

from .extensions import db
from .models import Task, PushSubscription
from .push import send_push


def _check_reminders_job():
    now = datetime.utcnow()
    # pick tasks with remind_at due and not already reminded
    tasks = Task.query.filter(Task.remind_at != None, Task.remind_at <= now, Task.reminded == False).all()
    for t in tasks:
        subs = PushSubscription.query.filter_by(user_id=t.user_id).all()
        for s in subs:
            title = f"Rappel: {t.title}"
            body = t.description or ''
            ok = send_push(s, title, body, {'task_id': t.id})
            # if not ok and status indicates gone, we could delete subscription (omitted)
        t.reminded = True
        db.session.commit()


def init_scheduler(app):
    scheduler = BackgroundScheduler()
    # schedule job every minute
    def job_wrapper():
        with app.app_context():
            _check_reminders_job()
    scheduler.add_job(job_wrapper, 'interval', seconds=60, id='reminder-check')
    scheduler.start()
    app.logger.info('Reminder scheduler started')
    return scheduler
