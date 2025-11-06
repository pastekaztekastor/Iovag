# 🍽️ Iovag - Gestionnaire de Recettes et Menus

**Ici on veille à la gourmandise**

Iovag est une plateforme **100% gratuite** et **open source** de gestion culinaire qui vous aide à organiser vos repas, gérer vos recettes et simplifier vos courses. Fini le stress de "qu'est-ce qu'on mange ce soir ?" !

## ✨ Fonctionnalités

- 📖 **Gestion de recettes** : Créez, organisez et évaluez vos recettes favorites avec filtres par type de repas et saison
- 📅 **Planification de menus** : Planifiez vos repas (petit-déjeuner, déjeuner, goûter, dîner) sur plusieurs jours ou semaines
- 🛒 **Liste de courses intelligente** : Génération automatique avec ajustement des quantités selon le nombre de convives
- 📦 **Gestion de stock** : Suivez vos ingrédients en stock et recevez des alertes pour les produits à racheter
- 🎯 **Ajustement automatique** : Les portions s'adaptent intelligemment au nombre de personnes
- ⭐ **Évaluation** : Notez vos recettes et retrouvez facilement vos favorites
- 👥 **Multi-utilisateurs** : Authentification sécurisée et données privées
- 🌍 **Communauté** : Partagez vos recettes avec d'autres passionnés (à venir)

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

## Plan de dev

Phase 1 : Setup (Semaine 1)

  - Init projet Flask
  - Config BDD et migrations
  - Authentification basique
  - Structure du projet

  Phase 2 : Recettes (Semaine 2)

  - CRUD recettes
  - Gestion ingrédients
  - Interface de recherche

  Phase 3 : Menus (Semaine 3)

  - CRUD menus
  - Assignation recettes
  - Vue calendrier

  Phase 4 : Liste de Courses (Semaine 4)

  - Génération automatique
  - Interface de gestion
  - Export PDF

  Phase 5 : Polish & Deploy (Semaine 5)

  - Tests
  - Design responsive
  - Déploiement (Heroku/Render/Railway)

## Fonctionnalités Futures (v2.0+)

  - 📊 Statistiques (recettes préférées, fréquence)
  - 🏪 Gestion du stock (éviter achats inutiles)
  - 📱 Mode hors-ligne (PWA)
  - 🔗 Partage de menus/recettes
  - 🌍 Import de recettes depuis URL
  - 📧 Email de la liste de courses
  - 🎨 Thèmes visuels personnalisables
  - 📅 Planification multi-semaines

## TODO

  1. Lancer l'application: FLASK_APP=run.py 
  venv/bin/flask run
  2. Créer un premier utilisateur
  3. Tester la création de recettes, menus et listes
  4. Implémenter l'export PDF des listes de courses
  (WeasyPrint)
  5. Ajouter la recherche/filtres côté client
  (JavaScript)
  6. Implémenter l'édition complète des
  ingrédients/instructions de recettes