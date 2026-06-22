"""
REST API blueprint (extended with push subscription endpoints)
"""
from flask import Blueprint, request, jsonify, current_app
from . import db
from .models import Task, Project, PushSubscription
from datetime import datetime
from flask_login import login_required, current_user

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/tasks', methods=['GET'])
@login_required
def list_tasks():
    status = request.args.get('status')
    project = request.args.get('project')
    q = Task.query.filter_by(user_id=current_user.id)
    if status:
        q = q.filter_by(status=status)
    if project:
        q = q.filter_by(project_id=project)
    tasks = [t.to_dict() for t in q.order_by(Task.created_at.desc()).all()]
    return jsonify(tasks)

@bp.route('/tasks/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    t = Task.query.get_or_404(task_id)
    if t.user_id != current_user.id:
        return jsonify({'error':'Not found'}), 404
    return jsonify(t.to_dict())

@bp.route('/tasks', methods=['POST'])
@login_required
def create_task():
    data = request.json
    t = Task(
        title=data.get('title','Untitled'),
        description=data.get('description'),
        status=data.get('status','todo'),
        favorite=data.get('favorite', False),
        project_id=data.get('project_id'),
        priority=data.get('priority', 0),
        tags=data.get('tags'),
        user_id=current_user.id,
    )
    due = data.get('due_date')
    if due:
        try:
            t.due_date = datetime.fromisoformat(due)
        except Exception:
            t.due_date = None
    remind = data.get('remind_at')
    if remind:
        try:
            t.remind_at = datetime.fromisoformat(remind)
        except Exception:
            t.remind_at = None
    db.session.add(t)
    db.session.commit()
    return jsonify(t.to_dict()), 201

@bp.route('/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    t = Task.query.get_or_404(task_id)
    if t.user_id != current_user.id:
        return jsonify({'error':'Not found'}), 404
    data = request.json
    t.title = data.get('title', t.title)
    t.description = data.get('description', t.description)
    t.status = data.get('status', t.status)
    t.favorite = data.get('favorite', t.favorite)
    t.project_id = data.get('project_id', t.project_id)
    t.priority = data.get('priority', t.priority)
    t.tags = data.get('tags', t.tags)
    due = data.get('due_date')
    if due is not None:
        try:
            t.due_date = datetime.fromisoformat(due) if due else None
        except Exception:
            pass
    remind = data.get('remind_at')
    if remind is not None:
        try:
            t.remind_at = datetime.fromisoformat(remind) if remind else None
        except Exception:
            pass
    db.session.commit()
    return jsonify(t.to_dict())

@bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    t = Task.query.get_or_404(task_id)
    if t.user_id != current_user.id:
        return jsonify({'error':'Not found'}), 404
    db.session.delete(t)
    db.session.commit()
    return '', 204

# Projects
@bp.route('/projects', methods=['GET'])
@login_required
def list_projects():
    projects = [p.to_dict() for p in Project.query.filter_by(user_id=current_user.id).order_by(Project.created_at.asc()).all()]
    return jsonify(projects)

@bp.route('/projects', methods=['POST'])
@login_required
def create_project():
    data = request.json
    p = Project(name=data.get('name','Untitled'), parent_id=data.get('parent_id'), user_id=current_user.id)
    db.session.add(p)
    db.session.commit()
    return jsonify(p.to_dict()), 201

@bp.route('/stats', methods=['GET'])
@login_required
def stats():
    total_done = Task.query.filter_by(status='done', user_id=current_user.id).count()
    total_en_cours = Task.query.filter_by(status='en_cours', user_id=current_user.id).count()
    total_todo = Task.query.filter_by(status='todo', user_id=current_user.id).count()
    # simple activity by created date (last 30 days)
    from sqlalchemy import func
    rows = db.session.query(func.date(Task.created_at), func.count(Task.id)).filter(Task.user_id==current_user.id).group_by(func.date(Task.created_at)).order_by(func.date(Task.created_at)).all()
    activity = [{'date': r[0].isoformat(), 'count': r[1]} for r in rows]
    return jsonify({
        'done': total_done,
        'en_cours': total_en_cours,
        'todo': total_todo,
        'activity': activity,
    })

# --- Push subscription endpoints ---
@bp.route('/vapid_public', methods=['GET'])
@login_required
def vapid_public():
    from os import getenv
    pub = getenv('VAPID_PUBLIC_KEY') or ''
    return jsonify({'publicKey': pub})

@bp.route('/subscribe', methods=['POST'])
@login_required
def subscribe():
    data = request.json
    endpoint = data.get('endpoint')
    keys = data.get('keys', {})
    p256dh = keys.get('p256dh')
    auth_key = keys.get('auth')
    if not endpoint or not p256dh or not auth_key:
        return jsonify({'error':'invalid payload'}), 400
    existing = PushSubscription.query.filter_by(endpoint=endpoint, user_id=current_user.id).first()
    if existing:
        return jsonify({'ok':True})
    s = PushSubscription(endpoint=endpoint, p256dh=p256dh, auth=auth_key, user_id=current_user.id)
    db.session.add(s)
    db.session.commit()
    return jsonify({'ok':True})

@bp.route('/unsubscribe', methods=['POST'])
@login_required
def unsubscribe():
    data = request.json
    endpoint = data.get('endpoint')
    if not endpoint:
        return jsonify({'error':'invalid payload'}), 400
    PushSubscription.query.filter_by(endpoint=endpoint, user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({'ok':True})

@bp.route('/push/test', methods=['POST'])
@login_required
def push_test():
    data = request.json or {}
    task_id = data.get('task_id')
    from .push import send_push
    subs = PushSubscription.query.filter_by(user_id=current_user.id).all()
    if not subs:
        return jsonify({'error':'no_subscriptions'}), 400
    from .models import Task
    t = Task.query.get(task_id) if task_id else None
    title = 'Todom test'
    body = t.title if t else 'Notification de test'
    results = []
    for s in subs:
        ok = send_push(s, title, body, {'task_id': t.id if t else None})
        results.append({'endpoint': s.endpoint, 'ok': ok})
    return jsonify({'results': results})
