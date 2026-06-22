"""
Simple helper to create / seed the database
"""
from backend import create_app
from backend.extensions import db
from backend.models import Project, Task, User
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    db.create_all()
    # create default user if none
    if User.query.count() == 0:
        u = User(username='admin', email='admin@example.com')
        u.set_password('password')
        db.session.add(u)
        db.session.commit()
        print('Created default user: admin / password')

    # seed minimal data if empty
    user = User.query.first()
    if Project.query.count() == 0:
        p1 = Project(name='Personal', user_id=user.id)
        p2 = Project(name='Work', user_id=user.id)
        p3 = Project(name='Inbox', user_id=user.id)
        db.session.add_all([p1,p2,p3])
        db.session.commit()
    if Task.query.count() == 0:
        p = Project.query.first()
        now = datetime.utcnow()
        t1 = Task(title='Découvrir le projet', description='Lire README, explorer code', status='todo', project=p, user_id=user.id)
        t2 = Task(title='Configurer environnement', description='Créer venv et installer dépendances', status='en_cours', project=p, favorite=True, user_id=user.id)
        t3 = Task(title='Tâche réalisée exemple', description='Exemple de tâche faite', status='done', project=p, user_id=user.id)
        db.session.add_all([t1,t2,t3])
        db.session.commit()
    print('DB initialized')
