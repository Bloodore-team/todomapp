# 📦 Guide de déploiement - Netlify + Supabase

## 🔧 Architecture

```
Netlify (Frontend)          Supabase (Backend)
  ├─ HTML/CSS/JS       ←→   ├─ Flask API
  ├─ Dashboard              ├─ PostgreSQL DB
  └─ Redirects              └─ Auth
```

---

## 📚 Étapes de déploiement

### **Phase 1: Configuration Supabase (Backend)**

#### 1. Créer un projet Supabase
- Allez sur https://supabase.com
- Cliquez sur "New Project"
- Complétez les informations

#### 2. Configurer la base de données PostgreSQL
```bash
# Récupérez vos credentials Supabase:
# - URL: https://xxxx.supabase.co
# - Clé anon: eyJhbGc...
# - Clé service_role: eyJhbGc...
```

#### 3. Cloner et préparer votre code
```bash
git clone https://github.com/Bloodore-team/todomapp.git
cd todomapp
python -m venv .venv
source .venv/bin/activate  # ou .\.venv\Scripts\activate sur Windows
pip install -r requirements.txt
```

#### 4. Définir les variables d'environnement
```bash
# Créez un fichier .env
cp .env.example .env

# Complétez avec vos credentialsSupabase:
DATABASE_URL=postgresql://postgres:[password]@db.supabase.co:5432/postgres
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

#### 5. Initialiser la base de données
```bash
python init_db.py
```

#### 6. Déployer le backend sur Supabase/Heroku/Railway
**Option A: Supabase (Functions)**
- Utilisez Supabase Edge Functions pour serverless Python

**Option B: Heroku (Recommandé pour Flask)**
```bash
heroku login
heroku create your-app-name
git push heroku main
```

**Option C: Railway.app**
- Connectez votre repo GitHub
- Railway déploiera automatiquement

---

### **Phase 2: Configuration Netlify (Frontend)**

#### 1. Extraire le frontend
- Créez un dossier `public/` avec votre HTML/CSS/JavaScript
- OU utilisez un framework (React, Vue, Svelte)

#### 2. Connecter à Netlify
```bash
# Option A: Via CLI
npm install -g netlify-cli
netlify deploy --prod

# Option B: Via dashboard Netlify
# - Connectez votre repo GitHub
# - Netlify déploiera à chaque push sur main
```

#### 3. Configurer les variables d'environnement Netlify
Dans Netlify Dashboard → Site settings → Build & deploy → Environment:
```
REACT_APP_API_URL=https://your-backend.herokuapp.com
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key
```

#### 4. Mettre à jour netlify.toml
- Le fichier `netlify.toml` est déjà configuren'est déjà configuré
- Il redirige les requêtes API vers votre backend

---

## 🔌 Configuration API CORS

Dans votre `run.py` ou configuration Flask, ajoutez:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://your-netlify-site.netlify.app"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

Installez: `pip install flask-cors`

---

## 🔐 Variables d'environnement requises

### **Backend (Supabase/Heroku)**
```
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=[génères une clé aléatoire]
DATABASE_URL=[PostgreSQL de Supabase]
SUPABASE_URL=[URL Supabase]
SUPABASE_ANON_KEY=[Clé anon]
FRONTEND_URL=https://your-netlify-site.netlify.app
VAPID_PUBLIC_KEY=[Généré par generate_vapid.py]
VAPID_PRIVATE_KEY=[Généré par generate_vapid.py]
```

### **Frontend (Netlify)**
```
REACT_APP_API_URL=https://your-backend.com
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=[Clé anon Supabase]
```

---

## 🧪 Tester localement avant déploiement

```bash
# Terminal 1: Backend Flask
export DATABASE_URL="postgresql://..."
python run.py

# Terminal 2: Frontend (si React/Vue/etc)
npm start

# Ouvrez http://localhost:3000 (frontend) ou http://localhost:5000 (backend)
```

---

## ✅ Checklist de déploiement

- [ ] Supabase project créé et DB initialisée
- [ ] Backend déployé (Heroku, Railway, ou Supabase Functions)
- [ ] Netlify repo connecté et domain configuré
- [ ] Variables d'environnement définies partout
- [ ] CORS configuré correctement
- [ ] Tests de bout-en-bout effectués
- [ ] SSL/HTTPS activé (automatique sur Netlify)
- [ ] Sauvegardes/backups configurées sur Supabase

---

## 🚨 Problèmes courants

### **CORS Error**
→ Vérifiez les origins dans flask-cors

### **Database connection failed**
→ Vérifiez `DATABASE_URL` et autorisez les IPs dans Supabase

### **Frontend ne voit pas l'API**
→ Vérifiez `REACT_APP_API_URL` et que le backend est en ligne

### **Notifications Web ne fonctionnent pas**
→ Régénérez VAPID keys avec `python generate_vapid.py`

---

## 📞 Support

- Supabase: https://supabase.com/docs
- Netlify: https://docs.netlify.com
- Flask: https://flask.palletsprojects.com
