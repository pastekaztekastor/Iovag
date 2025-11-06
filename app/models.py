"""
Modèles de base de données pour Iovag
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class UnitConverter:
    """Convertisseur d'unités pour normaliser les quantités d'ingrédients"""

    # Table de conversion : unité -> (unité_base, facteur_multiplication)
    CONVERSIONS = {
        # Masse
        'kg': ('g', 1000),
        'g': ('g', 1),
        'mg': ('g', 0.001),

        # Volume
        'l': ('ml', 1000),
        'ml': ('ml', 1),
        'cl': ('ml', 10),
        'dl': ('ml', 100),

        # Unités sans conversion directe (dépendent de l'ingrédient)
        'pièce': ('pièce', 1),
        'gousse': ('gousse', 1),
        'feuille': ('feuille', 1),
        'sachet': ('sachet', 1),
        'botte': ('botte', 1),
        'tranche': ('tranche', 1),
    }

    @classmethod
    def normaliser(cls, quantite, unite, ingredient=None):
        """
        Convertit une quantité dans son unité de base
        Pour les fruits & légumes avec poids estimé, convertit pièce → g

        Args:
            quantite: La quantité à convertir
            unite: L'unité actuelle
            ingredient: Objet Ingredient (optionnel, pour conversion pièce ↔ g)

        Returns:
            tuple (quantite_normalisee, unite_base)
        """
        if not unite:
            return quantite, None

        unite_lower = unite.lower()

        # Si c'est une pièce et qu'on a un poids estimé, convertir en grammes
        if unite_lower == 'pièce' and ingredient and ingredient.poids_estime_g:
            return quantite * ingredient.poids_estime_g, 'g'

        if unite_lower in cls.CONVERSIONS:
            unite_base, facteur = cls.CONVERSIONS[unite_lower]
            return quantite * facteur, unite_base

        # Si l'unité n'est pas reconnue, retourner telle quelle
        return quantite, unite

    @classmethod
    def convertir_pour_affichage(cls, quantite, unite, ingredient=None):
        """
        Convertit une quantité pour l'affichage
        Pour les fruits & légumes avec poids estimé, convertit g → pièce

        Args:
            quantite: La quantité en unité de base
            unite: L'unité de base
            ingredient: Objet Ingredient (optionnel)

        Returns:
            tuple (quantite_affichage, unite_affichage, quantite_detail_g)
        """
        # Si c'est un ingrédient avec poids estimé en grammes, afficher en pièces
        if unite == 'g' and ingredient and ingredient.poids_estime_g:
            nb_pieces = quantite / ingredient.poids_estime_g
            return nb_pieces, 'pièce', quantite

        # Sinon, retourner tel quel
        return quantite, unite, None

    @classmethod
    def peuvent_etre_additionnees(cls, unite1, unite2, ingredient=None):
        """
        Vérifie si deux unités peuvent être additionnées (même unité de base)

        Args:
            unite1: Première unité
            unite2: Deuxième unité
            ingredient: Objet Ingredient (optionnel)

        Returns:
            bool: True si les unités peuvent être additionnées
        """
        if not unite1 or not unite2:
            return unite1 == unite2

        _, base1 = cls.normaliser(1, unite1, ingredient)
        _, base2 = cls.normaliser(1, unite2, ingredient)

        return base1 == base2


@login_manager.user_loader
def load_user(user_id):
    """Callback pour charger un utilisateur"""
    return User.query.get(int(user_id))


# Table d'association pour les recettes favorites
recettes_favorites = db.Table('recettes_favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('recette_id', db.Integer, db.ForeignKey('recettes.id'), primary_key=True),
    db.Column('added_at', db.DateTime, default=datetime.utcnow)
)


class User(UserMixin, db.Model):
    """Modèle utilisateur"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    onboarding_completed = db.Column(db.Boolean, default=False)

    # Relations
    recettes = db.relationship('Recette', backref='auteur', lazy='dynamic', cascade='all, delete-orphan', foreign_keys='Recette.created_by')
    menus = db.relationship('Menu', backref='auteur', lazy='dynamic', cascade='all, delete-orphan')
    stock = db.relationship('Stock', backref='utilisateur', lazy='dynamic', cascade='all, delete-orphan')
    recettes_sauvegardees = db.relationship('Recette', secondary=recettes_favorites, backref='utilisateurs_sauvegardes', lazy='dynamic')

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
    lieu_rangement = db.Column(db.String(100))  # Où est rangé l'ingrédient (frigo, placard, congélateur, etc.)
    mois_saison = db.Column(db.String(200))  # Mois de saison pour fruits/légumes (format: "Janvier,Février,Mars")
    stock_limite = db.Column(db.Float)  # Quantité minimale en stock, seuil d'alerte
    poids_estime_g = db.Column(db.Float)  # Poids estimé d'une pièce en grammes (pour conversion pièce ↔ g)
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

    # Mois de l'année
    MOIS = [
        'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
    ]

    def get_mois_saison_list(self):
        """Retourne la liste des mois de saison"""
        if not self.mois_saison:
            return []
        return [m.strip() for m in self.mois_saison.split(',') if m.strip()]

    def set_mois_saison_list(self, mois_list):
        """Définit les mois de saison à partir d'une liste"""
        if mois_list:
            self.mois_saison = ','.join(mois_list)
        else:
            self.mois_saison = None

    def est_de_saison(self, mois=None):
        """Vérifie si l'ingrédient est de saison pour un mois donné (ou le mois actuel)"""
        if not self.mois_saison:
            return True  # Si pas de mois défini, toujours de saison

        if mois is None:
            from datetime import datetime
            mois = self.MOIS[datetime.now().month - 1]

        return mois in self.get_mois_saison_list()

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
    mois_saison = db.Column(db.String(200))  # Mois de saison basés sur les ingrédients (format: "Janvier,Février,Mars")
    type_repas = db.Column(db.String(200))  # Type de repas (format: "Petit-déjeuner,Déjeuner,Goûter,Dîner")
    is_public = db.Column(db.Boolean, default=True)  # Si True, visible par tous les membres
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relations
    ingredients = db.relationship('RecetteIngredient', backref='recette', lazy='dynamic', cascade='all, delete-orphan')
    instructions = db.relationship('Instruction', backref='recette', lazy='dynamic', cascade='all, delete-orphan', order_by='Instruction.ordre')

    # Types de repas prédéfinis
    TYPES_REPAS = ['Petit-déjeuner', 'Déjeuner', 'Goûter', 'Dîner']

    def calculer_mois_saison_auto(self):
        """
        Calcule automatiquement les mois de saison en fonction des ingrédients
        Retourne l'intersection des mois de tous les ingrédients saisonniers
        Si aucun ingrédient n'a de mois défini, retourne tous les mois
        """
        mois_tous = set(Ingredient.MOIS)
        mois_intersection = None

        for ri in self.ingredients:
            ingredient = ri.ingredient
            if ingredient and ingredient.mois_saison:
                mois_ing = set(ingredient.get_mois_saison_list())
                if mois_ing:  # Si l'ingrédient a des mois définis
                    if mois_intersection is None:
                        mois_intersection = mois_ing
                    else:
                        mois_intersection = mois_intersection.intersection(mois_ing)

        # Si aucun ingrédient saisonnier ou intersection vide, disponible toute l'année
        if mois_intersection is None or len(mois_intersection) == 0:
            return []

        # Retourner les mois dans l'ordre
        return [m for m in Ingredient.MOIS if m in mois_intersection]

    def get_mois_saison_list(self):
        """Retourne la liste des mois de saison"""
        if not self.mois_saison:
            return []
        return [m.strip() for m in self.mois_saison.split(',') if m.strip()]

    def set_mois_saison_list(self, mois_list):
        """Définit les mois de saison à partir d'une liste"""
        if mois_list:
            self.mois_saison = ','.join(mois_list)
        else:
            self.mois_saison = None

    def get_type_repas_list(self):
        """Retourne la liste des types de repas"""
        if not self.type_repas:
            return []
        return [t.strip() for t in self.type_repas.split(',') if t.strip()]

    def set_type_repas_list(self, types_list):
        """Définit les types de repas à partir d'une liste"""
        if types_list:
            self.type_repas = ','.join(types_list)
        else:
            self.type_repas = None

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

    def get_affichage_avec_poids(self):
        """
        Retourne l'affichage avec le poids estimé entre parenthèses
        Ex: "3 pièces (~450g)" ou "250 g"

        Returns:
            str: Quantité formatée avec poids estimé si applicable
        """
        import math

        # Si c'est en pièces et qu'on a un poids estimé, afficher le poids
        if self.unite and self.unite.lower() == 'pièce' and self.ingredient.poids_estime_g:
            poids_total = self.quantite * self.ingredient.poids_estime_g
            qte_arrondie = math.ceil(self.quantite) if self.quantite > 1 else self.quantite
            poids_arrondi = math.ceil(poids_total)

            # Pluriel si nécessaire
            if qte_arrondie > 1:
                return f"{qte_arrondie:.0f} pièces (~{poids_arrondi}g)"
            else:
                return f"{qte_arrondie:.1f} pièce (~{poids_arrondi}g)"

        # Sinon affichage standard
        if self.quantite == int(self.quantite):
            return f"{int(self.quantite)} {self.unite}"
        else:
            return f"{self.quantite:.1f} {self.unite}"

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

        IMPORTANT: À la génération initiale, TOUS les ingrédients sont ajoutés
        sans déduction du stock. La déduction du stock se fait dans la phase
        "réviser" via la méthode verifier_stock() de ListeCourse.
        """
        ingredients_totaux = {}

        # Parcourir tous les jours et tous les repas
        for jour in self.jours:
            for repas_type in ['petit_dejeuner', 'dejeuner', 'gouter', 'diner']:
                recette = getattr(jour, f'{repas_type}_recette', None)
                if recette:
                    # Calculer les ingrédients ajustés pour le nombre de personnes du menu
                    ingredients_ajustes = recette.get_ingredients_for_portions(self.nb_personnes)

                    for ingredient, quantite, unite in ingredients_ajustes:
                        # Normaliser l'unité pour regrouper les quantités
                        quantite_normalisee, unite_base = UnitConverter.normaliser(quantite, unite, ingredient)

                        key = (ingredient.id, unite_base)
                        if key in ingredients_totaux:
                            ingredients_totaux[key]['quantite'] += quantite_normalisee
                        else:
                            ingredients_totaux[key] = {
                                'ingredient': ingredient,
                                'quantite': quantite_normalisee,
                                'unite': unite_base
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

        # Créer TOUS les items sans déduction du stock (brouillon)
        # La déduction se fera lors de la révision
        for data in ingredients_totaux.values():
            item = ListeCourseItem(
                liste_id=liste.id,
                nom_ingredient=data['ingredient'].nom,
                quantite=data['quantite'],
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
    gouter_id = db.Column(db.Integer, db.ForeignKey('recettes.id'), nullable=True)
    diner_id = db.Column(db.Integer, db.ForeignKey('recettes.id'), nullable=True)

    # Relations
    petit_dejeuner_recette = db.relationship('Recette', foreign_keys=[petit_dejeuner_id])
    dejeuner_recette = db.relationship('Recette', foreign_keys=[dejeuner_id])
    gouter_recette = db.relationship('Recette', foreign_keys=[gouter_id])
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
    statut = db.Column(db.String(20), default='brouillon')  # brouillon, validee, en_course, terminee
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relations
    ingredients = db.relationship('ListeCourseItem', backref='liste', lazy='dynamic', cascade='all, delete-orphan')

    def verifier_stock(self):
        """
        Vérifier le stock pour chaque ingrédient et calculer quantite_en_stock
        Cette méthode est appelée lors de la phase "réviser"
        Les items ne sont PAS supprimés automatiquement, l'utilisateur décide
        """
        from app.models import Stock, Ingredient

        for item in self.ingredients.all():
            # Trouver l'ingrédient dans la base
            ingredient = Ingredient.query.filter_by(nom=item.nom_ingredient).first()
            if ingredient:
                # Chercher le stock de l'utilisateur pour cet ingrédient
                stock_item = Stock.query.filter_by(
                    user_id=self.created_by,
                    ingredient_id=ingredient.id
                ).first()

                if stock_item:
                    # Normaliser le stock pour comparer avec la quantité nécessaire
                    stock_normalise, stock_unite_base = UnitConverter.normaliser(
                        stock_item.quantite, stock_item.unite, ingredient
                    )

                    # Normaliser la quantité nécessaire
                    qte_necessaire_norm, qte_unite_base = UnitConverter.normaliser(
                        item.quantite, item.unite, ingredient
                    )

                    # Si les unités correspondent, stocker le stock
                    if stock_unite_base == qte_unite_base:
                        item.quantite_en_stock = stock_normalise
                    else:
                        # Unités incompatibles
                        item.quantite_en_stock = 0
                else:
                    # Pas de stock
                    item.quantite_en_stock = 0
            else:
                item.quantite_en_stock = 0

    def retirer_items_en_stock(self):
        """
        Retirer tous les items dont le stock est suffisant
        Cette méthode est appelée manuellement par l'utilisateur
        """
        from app.models import Ingredient

        items_a_supprimer = []

        for item in self.ingredients.all():
            # Si quantite_en_stock >= quantite nécessaire, marquer pour suppression
            if item.quantite_en_stock is not None and item.quantite_en_stock > 0:
                ingredient = Ingredient.query.filter_by(nom=item.nom_ingredient).first()

                if ingredient:
                    # Normaliser pour comparer
                    qte_necessaire_norm, qte_unite_base = UnitConverter.normaliser(
                        item.quantite, item.unite, ingredient
                    )
                    stock_normalise, stock_unite_base = UnitConverter.normaliser(
                        item.quantite_en_stock, item.unite, ingredient
                    )

                    # Si stock suffisant, marquer pour suppression
                    if stock_unite_base == qte_unite_base and stock_normalise >= qte_necessaire_norm:
                        items_a_supprimer.append(item)

        # Supprimer les items
        for item in items_a_supprimer:
            db.session.delete(item)

        return len(items_a_supprimer)

    def valider(self):
        """Marquer la liste comme validée (prête pour les courses)"""
        self.statut = 'validee'

    def commencer_courses(self):
        """Commencer les courses (passage en magasin)"""
        self.statut = 'en_course'
        # Initialiser quantite_achetee avec quantite pour chaque item
        for item in self.ingredients.all():
            if item.quantite_achetee is None:
                item.quantite_achetee = item.quantite

    def confirmer(self):
        """Confirmer l'achat et mettre à jour le stock avec les quantités ACHETÉES"""
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

                    # Utiliser quantite_achetee si disponible, sinon quantite
                    quantite_a_ajouter = item.quantite_achetee if item.quantite_achetee is not None else item.quantite

                    if stock_item:
                        # Ajouter à la quantité existante
                        stock_item.quantite += quantite_a_ajouter
                        stock_item.unite = item.unite
                    else:
                        # Créer un nouveau stock
                        stock_item = Stock(
                            user_id=self.created_by,
                            ingredient_id=ingredient.id,
                            quantite=quantite_a_ajouter,
                            unite=item.unite
                        )
                        db.session.add(stock_item)

        self.statut = 'terminee'

    def __repr__(self):
        return f'<ListeCourse {self.nom}>'


class ListeCourseItem(db.Model):
    """Modèle item de liste de courses"""
    __tablename__ = 'liste_course_items'

    id = db.Column(db.Integer, primary_key=True)
    liste_id = db.Column(db.Integer, db.ForeignKey('liste_courses.id'), nullable=False)
    nom_ingredient = db.Column(db.String(100), nullable=False)
    quantite = db.Column(db.Float, nullable=False)  # Quantité nécessaire (de la recette)
    quantite_en_stock = db.Column(db.Float, nullable=True)  # Quantité présumée en stock (calculée automatiquement)
    quantite_achetee = db.Column(db.Float, nullable=True)  # Quantité réellement achetée
    unite = db.Column(db.String(20))
    rayon = db.Column(db.String(50))  # Pour organiser la liste par rayon
    achete = db.Column(db.Boolean, default=False)

    def get_quantite_arrondie(self):
        """Retourne la quantité arrondie à l'unité supérieure pour l'affichage en magasin"""
        import math
        if self.quantite_achetee is not None:
            return math.ceil(float(self.quantite_achetee)) if self.quantite_achetee > 0 else 0
        return math.ceil(float(self.quantite)) if self.quantite > 0 else 0

    def get_quantite_manquante(self):
        """Retourne la quantité manquante (nécessaire - en stock)"""
        if self.quantite_en_stock is None:
            return self.quantite
        manquante = self.quantite - self.quantite_en_stock
        return max(0, manquante)  # Ne pas retourner de valeur négative

    def get_quantite_manquante_arrondie(self):
        """Retourne la quantité manquante arrondie à l'unité supérieure"""
        import math
        qte_manquante = self.get_quantite_manquante()
        if qte_manquante <= 0:
            return 0
        return math.ceil(float(qte_manquante))

    def get_lieu_rangement(self):
        """Retourne le lieu de rangement de l'ingrédient"""
        ingredient = Ingredient.query.filter_by(nom=self.nom_ingredient).first()
        if ingredient and ingredient.lieu_rangement:
            return ingredient.lieu_rangement
        return "Autre"

    def get_affichage_quantite(self):
        """
        Retourne la quantité formatée pour l'affichage
        Pour les fruits & légumes : affiche en pièces avec le poids entre parenthèses
        Pour les autres : affiche la quantité normale

        Returns:
            str: Quantité formatée (ex: "3 pièces (~450g)" ou "250 g")
        """
        import math
        ingredient = Ingredient.query.filter_by(nom=self.nom_ingredient).first()

        if ingredient:
            # Convertir pour affichage (g → pièce si applicable)
            qte_affichage, unite_affichage, poids_g = UnitConverter.convertir_pour_affichage(
                self.quantite, self.unite, ingredient
            )

            if poids_g is not None:
                # C'est un ingrédient avec poids estimé : afficher pièces + poids
                nb_pieces_arrondi = math.ceil(qte_affichage)
                poids_arrondi = math.ceil(poids_g)
                return f"{nb_pieces_arrondi} {unite_affichage}{'s' if nb_pieces_arrondi > 1 else ''} (~{poids_arrondi}g)"
            else:
                # Affichage normal
                if self.unite in ['g', 'ml']:
                    qte_arrondie = math.ceil(self.quantite)
                    return f"{qte_arrondie} {self.unite}"
                else:
                    return f"{self.quantite:.1f} {self.unite}"
        else:
            # Ingrédient non trouvé, affichage par défaut
            return f"{self.quantite:.1f} {self.unite}"

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

    # Seuils par défaut par catégorie
    SEUILS_DEFAUT = {
        'Fruits & Légumes': 200,
        'Viandes & Poissons': 200,
        'Produits laitiers': 100,
        'Épicerie salée': 100,
        'Épicerie sucrée': 100,
        'Surgelés': 200,
        'Boissons': 250,
        'Pain & Viennoiseries': 1,
        'Condiments & Sauces': 50,
        'Herbes & Épices': 10,
        'Conserves': 1,
        'Pâtes & Riz': 200,
        'Huiles & Vinaigres': 100,
        'Autre': 50
    }

    def get_seuil_stock(self):
        """
        Retourne le seuil de stock à utiliser pour cet item
        Utilise stock_limite de l'ingrédient si défini, sinon seuil par défaut
        """
        if self.ingredient.stock_limite is not None:
            return self.ingredient.stock_limite

        # Seuil par défaut selon catégorie
        categorie = self.ingredient.categorie or 'Autre'
        return self.SEUILS_DEFAUT.get(categorie, 50)

    def est_stock_bas(self):
        """Vérifie si le stock est en dessous du seuil"""
        return self.quantite <= self.get_seuil_stock()

    def __repr__(self):
        return f'<Stock {self.quantite} {self.unite}>'


class Inventaire(db.Model):
    """Modèle pour l'historique des inventaires"""
    __tablename__ = 'inventaires'

    id = db.Column(db.Integer, primary_key=True)
    date_inventaire = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    items = db.relationship('InventaireItem', backref='inventaire', lazy='dynamic', cascade='all, delete-orphan')

    def get_total_ecarts(self):
        """Retourne le nombre total d'écarts (positifs et négatifs)"""
        ecarts_positifs = sum(1 for item in self.items if item.ecart > 0)
        ecarts_negatifs = sum(1 for item in self.items if item.ecart < 0)
        return {
            'positifs': ecarts_positifs,
            'negatifs': ecarts_negatifs,
            'total': ecarts_positifs + ecarts_negatifs
        }

    def get_ingredients_manquants(self):
        """Retourne la liste des ingrédients avec écarts négatifs"""
        return [item for item in self.items if item.ecart < 0]

    def get_ingredients_surplus(self):
        """Retourne la liste des ingrédients avec écarts positifs"""
        return [item for item in self.items if item.ecart > 0]

    def __repr__(self):
        return f'<Inventaire {self.date_inventaire.strftime("%Y-%m-%d %H:%M")}>'


class InventaireItem(db.Model):
    """Modèle pour les items d'un inventaire"""
    __tablename__ = 'inventaire_items'

    id = db.Column(db.Integer, primary_key=True)
    inventaire_id = db.Column(db.Integer, db.ForeignKey('inventaires.id', ondelete='CASCADE'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable=False)
    quantite_theorique = db.Column(db.Float, nullable=False)
    quantite_reelle = db.Column(db.Float, nullable=False)
    ecart = db.Column(db.Float, nullable=False)  # quantite_reelle - quantite_theorique
    unite = db.Column(db.String(20), nullable=False)

    # Relation vers l'ingrédient
    ingredient = db.relationship('Ingredient', backref='inventaire_items')

    def get_ecart_pourcentage(self):
        """Retourne l'écart en pourcentage"""
        if self.quantite_theorique == 0:
            return 0
        return (self.ecart / self.quantite_theorique) * 100

    def get_affichage_quantites(self):
        """Retourne un dictionnaire avec les quantités formatées"""
        return {
            'theorique': f"{self.quantite_theorique:.1f} {self.unite}",
            'reelle': f"{self.quantite_reelle:.1f} {self.unite}",
            'ecart': f"{self.ecart:+.1f} {self.unite}",  # +/- devant
            'ecart_pourcent': f"{self.get_ecart_pourcentage():+.1f}%"
        }

    def __repr__(self):
        return f'<InventaireItem {self.ingredient.nom}: {self.ecart:+.1f} {self.unite}>'


class ContactMessage(db.Model):
    """Messages de contact envoyés via le formulaire"""
    __tablename__ = 'contact_messages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)
    replied = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<ContactMessage from {self.email}: {self.subject}>'

    def to_dict(self):
        """Convertit le message en dictionnaire"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'subject': self.subject,
            'message': self.message,
            'created_at': self.created_at.isoformat(),
            'read': self.read,
            'replied': self.replied
        }
