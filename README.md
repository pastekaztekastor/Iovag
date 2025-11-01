# 🍽️ Iovag

**Ici on veille à la gourmandise**

Application web de gestion de menus hebdomadaires et de recettes avec génération automatique de listes de courses.

## 🎯 Fonctionnalités

- 📖 Gestion de recettes avec ingrédients et instructions
- 📅 Création de menus hebdomadaires
- 🛒 Génération automatique de listes de courses
- 📊 Gestion intelligente des portions (ajustement automatique des quantités)
- ⭐ Évaluation et notes sur les recettes
- 📄 Export PDF (menus, recettes, listes de courses)
- 👤 Multi-utilisateurs avec authentification

## 🚀 Installation

### Prérequis

- Python 3.10+
- pip

### Configuration

1. Cloner le repository
```bash
git clone <url>
cd Iovag
```

2. Créer un environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installer les dépendances
```bash
pip install -r requirements.txt
```

4. Configurer les variables d'environnement
```bash
cp .env.example .env
# Éditer .env avec vos configurations
```

5. Initialiser la base de données
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. Lancer l'application
```bash
python run.py
```

L'application sera accessible sur `http://localhost:5000`

## 📁 Structure du Projet

```
Iovag/
├── app/                    # Application Flask
│   ├── __init__.py        # Factory
│   ├── models.py          # Modèles SQLAlchemy
│   ├── routes/            # Routes/Controllers
│   ├── templates/         # Templates Jinja2
│   └── static/            # Fichiers statiques (CSS, JS, images)
├── migrations/            # Migrations Alembic
├── tests/                 # Tests unitaires
├── config.py              # Configuration
├── requirements.txt       # Dépendances
└── run.py                 # Point d'entrée
```

## 🛠️ Technologies

- **Backend:** Flask, SQLAlchemy
- **Frontend:** Bootstrap 5, Jinja2
- **Base de données:** SQLite (dev), PostgreSQL (prod)
- **PDF:** WeasyPrint

## 📝 Licence

MIT

## 👨‍💻 Auteur

Mathurin Champémont
