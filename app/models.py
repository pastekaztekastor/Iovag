"""
Modèles de base de données pour Iovag
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    """Callback pour charger un utilisateur"""
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """Modèle utilisateur"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    recettes = db.relationship('Recette', backref='auteur', lazy='dynamic', cascade='all, delete-orphan')
    menus = db.relationship('Menu', backref='auteur', lazy='dynamic', cascade='all, delete-orphan')
    stock = db.relationship('Stock', backref='utilisateur', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hasher le mot de passe"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Vérifier le mot de passe"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Ingredient(db.Model):
    """Modèle ingrédient"""
    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False, unique=True, index=True)
    categorie = db.Column(db.String(50), nullable=True, index=True)  # Rayon magasin: Fruits & Légumes, Viandes, etc.
    unite_mesure = db.Column(db.String(20))  # g, ml, pièce, etc.
    duree_conservation = db.Column(db.Integer)  # Durée en jours
    #lieu_rangement = db.Column(db.String(100))  # Où est rangé l'ingrédient (frigo, placard, congélateur, etc.)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    recette_ingredients = db.relationship('RecetteIngredient', backref='ingredient', lazy='dynamic')
    stock = db.relationship('Stock', backref='ingredient', lazy='dynamic')

    # Catégories prédéfinies pour les rayons magasin
    CATEGORIES = [
        'Fruits & Légumes',
        'Viandes & Poissons',
        'Produits laitiers',
        'Épicerie salée',
        'Épicerie sucrée',
        'Surgelés',
        'Boissons',
        'Pain & Viennoiseries',
        'Condiments & Sauces',
        'Herbes & Épices',
        'Conserves',
        'Pâtes & Riz',
        'Huiles & Vinaigres',
        'Autre'
    ]

    # Lieux de rangement prédéfinis
    LIEUX_RANGEMENT = [
        'Frigo (haut)',
        'Frigo (milieu)',
        'Frigo (bas)',
        'Frigo (bac à légumes)',
        'Frigo (porte)',
        'Congélateur',
        'Placard sec',
        'Placard épices',
        'Corbeille à fruits',
        'Cave',
        'Autre'
    ]

    def __repr__(self):
        return f'<Ingredient {self.nom}>'


class Recette(db.Model):
    """Modèle recette"""
    __tablename__ = 'recettes'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False, index=True)
    portions = db.Column(db.Integer, default=4)  # Nombre de portions de base
    temps_preparation = db.Column(db.String(50))  # Ex: "15 min"
    temps_cuisson = db.Column(db.String(50))  # Ex: "30 min"
    evaluation = db.Column(db.Integer, default=0)  # 0-5 étoiles
    auteur_nom = db.Column(db.String(100))  # Nom de l'auteur de la recette
    note = db.Column(db.Text)  # Notes personnelles
    photo_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relations
    ingredients = db.relationship('RecetteIngredient', backref='recette', lazy='dynamic', cascade='all, delete-orphan')
    instructions = db.relationship('Instruction', backref='recette', lazy='dynamic', cascade='all, delete-orphan', order_by='Instruction.ordre')

    def get_ingredients_for_portions(self, nb_portions):
        """
        Calcule les quantités d'ingrédients pour un nombre de portions donné

        Args:
            nb_portions: Nombre de portions souhaité

        Returns:
            Liste de tuples (ingredient, quantite_ajustee, unite)
        """
        ratio = nb_portions / self.portions
        ingredients_ajustes = []

        for ri in self.ingredients:
            quantite_ajustee = ri.quantite * ratio
            ingredients_ajustes.append((ri.ingredient, quantite_ajustee, ri.unite))

        return ingredients_ajustes

    def __repr__(self):
        return f'<Recette {self.nom}>'


class RecetteIngredient(db.Model):
    """Table d'association recette-ingrédient avec quantité"""
    __tablename__ = 'recette_ingredients'

    id = db.Column(db.Integer, primary_key=True)
    recette_id = db.Column(db.Integer, db.ForeignKey('recettes.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable=False)
    quantite = db.Column(db.Float, nullable=False)
    unite = db.Column(db.String(20))  # g, ml, pièce, etc.

    def __repr__(self):
        return f'<RecetteIngredient {self.quantite} {self.unite}>'


class Instruction(db.Model):
    """Modèle instruction de recette"""
    __tablename__ = 'instructions'

    id = db.Column(db.Integer, primary_key=True)
    recette_id = db.Column(db.Integer, db.ForeignKey('recettes.id'), nullable=False)
    ordre = db.Column(db.Integer, nullable=False)
    texte = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Instruction {self.ordre}>'


class Menu(db.Model):
    """Modèle menu"""
    __tablename__ = 'menus'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)  # Ex: "Menu Cocon d'Automne"
    date_debut = db.Column(db.Date, nullable=False, index=True)  # Premier jour du menu
    nb_personnes = db.Column(db.Integer, default=2)  # Nombre de personnes pour ce menu
    theme = db.Column(db.String(200))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relations
    jours = db.relationship('MenuJour', backref='menu', lazy='dynamic', cascade='all, delete-orphan', order_by='MenuJour.jour_semaine')
    listes_courses = db.relationship('ListeCourse', backref='menu', lazy='dynamic', cascade='all, delete-orphan')

    def generer_liste_courses(self):
        """
        Génère automatiquement la liste de courses pour ce menu
        en ajustant les quantités selon le nombre de personnes
        """
        ingredients_totaux = {}

        # Parcourir tous les jours et tous les repas
        for jour in self.jours:
            for repas_type in ['petit_dejeuner', 'dejeuner', 'diner']:
                recette = getattr(jour, f'{repas_type}_recette', None)
                if recette:
                    # Calculer les ingrédients ajustés pour le nombre de personnes du menu
                    ingredients_ajustes = recette.get_ingredients_for_portions(self.nb_personnes)

                    for ingredient, quantite, unite in ingredients_ajustes:
                        key = (ingredient.id, unite)
                        if key in ingredients_totaux:
                            ingredients_totaux[key]['quantite'] += quantite
                        else:
                            ingredients_totaux[key] = {
                                'ingredient': ingredient,
                                'quantite': quantite,
                                'unite': unite
                            }

        # Créer une nouvelle liste de courses
        from datetime import datetime
        liste = ListeCourse(
            nom=f"Liste de courses - {self.nom}",
            menu_id=self.id,
            created_by=self.created_by
        )
        db.session.add(liste)
        db.session.flush()  # Pour obtenir l'ID

        # Créer les items en vérifiant le stock
        for data in ingredients_totaux.values():
            quantite_necessaire = data['quantite']

            # Vérifier le stock pour cet ingrédient
            stock_item = Stock.query.filter_by(
                user_id=self.created_by,
                ingredient_id=data['ingredient'].id
            ).first()

            if stock_item and stock_item.unite == data['unite']:
                # Si on a du stock avec la même unité, déduire la quantité
                quantite_necessaire -= stock_item.quantite

            # N'ajouter l'item que s'il reste une quantité à acheter
            if quantite_necessaire > 0:
                item = ListeCourseItem(
                    liste_id=liste.id,
                    nom_ingredient=data['ingredient'].nom,
                    quantite=quantite_necessaire,
                    unite=data['unite'],
                    rayon=data['ingredient'].categorie,
                    achete=False
                )
                db.session.add(item)

        return liste

    def __repr__(self):
        return f'<Menu {self.nom}>'


class MenuJour(db.Model):
    """Modèle jour de menu"""
    __tablename__ = 'menu_jours'

    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id'), nullable=False)
    jour_semaine = db.Column(db.Integer, nullable=False)  # 0=Lundi, 6=Dimanche

    # Recettes pour chaque repas (nullable car tous les repas ne sont pas toujours planifiés)
    petit_dejeuner_id = db.Column(db.Integer, db.ForeignKey('recettes.id'), nullable=True)
    dejeuner_id = db.Column(db.Integer, db.ForeignKey('recettes.id'), nullable=True)
    diner_id = db.Column(db.Integer, db.ForeignKey('recettes.id'), nullable=True)

    # Relations
    petit_dejeuner_recette = db.relationship('Recette', foreign_keys=[petit_dejeuner_id])
    dejeuner_recette = db.relationship('Recette', foreign_keys=[dejeuner_id])
    diner_recette = db.relationship('Recette', foreign_keys=[diner_id])

    @property
    def nom_jour(self):
        """Retourne le nom du jour en français"""
        jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        return jours[self.jour_semaine]

    def __repr__(self):
        return f'<MenuJour {self.nom_jour}>'


class ListeCourse(db.Model):
    """Modèle liste de courses (conteneur)"""
    __tablename__ = 'liste_courses'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id'), nullable=True)
    statut = db.Column(db.String(20), default='brouillon')  # brouillon, validee, confirmee
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relations
    ingredients = db.relationship('ListeCourseItem', backref='liste', lazy='dynamic', cascade='all, delete-orphan')

    def valider(self):
        """Marquer la liste comme validée (prête pour les courses)"""
        self.statut = 'validee'

    def confirmer(self):
        """Confirmer l'achat et mettre à jour le stock"""
        from app.models import Stock
        for item in self.ingredients.all():
            if item.achete:
                # Chercher si l'ingrédient existe dans le stock
                ingredient = Ingredient.query.filter_by(nom=item.nom_ingredient).first()
                if ingredient:
                    stock_item = Stock.query.filter_by(
                        user_id=self.created_by,
                        ingredient_id=ingredient.id
                    ).first()

                    if stock_item:
                        # Ajouter à la quantité existante
                        stock_item.quantite += item.quantite
                        stock_item.unite = item.unite
                    else:
                        # Créer un nouveau stock
                        stock_item = Stock(
                            user_id=self.created_by,
                            ingredient_id=ingredient.id,
                            quantite=item.quantite,
                            unite=item.unite
                        )
                        db.session.add(stock_item)

        self.statut = 'confirmee'

    def __repr__(self):
        return f'<ListeCourse {self.nom}>'


class ListeCourseItem(db.Model):
    """Modèle item de liste de courses"""
    __tablename__ = 'liste_course_items'

    id = db.Column(db.Integer, primary_key=True)
    liste_id = db.Column(db.Integer, db.ForeignKey('liste_courses.id'), nullable=False)
    nom_ingredient = db.Column(db.String(100), nullable=False)
    quantite = db.Column(db.Float, nullable=False)
    unite = db.Column(db.String(20))
    rayon = db.Column(db.String(50))  # Pour organiser la liste par rayon
    achete = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<ListeCourseItem {self.quantite} {self.unite} {self.nom_ingredient}>'


class Stock(db.Model):
    """Modèle stock utilisateur"""
    __tablename__ = 'stock'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable=False)
    quantite = db.Column(db.Float, nullable=False)
    unite = db.Column(db.String(20))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Stock {self.quantite} {self.unite}>'
