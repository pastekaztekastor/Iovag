#!/usr/bin/env python3
"""
Script pour compléter les informations des ingrédients existants
Ajoute catégories, lieux de rangement, mois de saison, poids estimés, etc.
"""
from app import create_app, db
from app.models import Ingredient

app = create_app()
app.app_context().push()

# Données complètes pour chaque ingrédient
INGREDIENTS_DATA = {
    # Viandes & Poissons
    'Lotte (queue)': {
        'categorie': 'Viandes & Poissons',
        'unite_mesure': 'g',
        'lieu_rangement': 'Frigo (bas)',
        'duree_conservation': 2,
        'mois_saison': 'Janvier,Février,Mars,Avril,Mai,Octobre,Novembre,Décembre',
        'stock_limite': 0,
        'poids_estime_g': None
    },
    'Jambon cru': {
        'categorie': 'Viandes & Poissons',
        'unite_mesure': 'tranches',
        'lieu_rangement': 'Frigo (milieu)',
        'duree_conservation': 7,
        'mois_saison': None,
        'stock_limite': 4,
        'poids_estime_g': 30  # 1 tranche = ~30g
    },
    'Poisson fumé': {
        'categorie': 'Viandes & Poissons',
        'unite_mesure': 'g',
        'lieu_rangement': 'Frigo (bas)',
        'duree_conservation': 10,
        'mois_saison': None,
        'stock_limite': 0,
        'poids_estime_g': None
    },
    'Lardons fumés': {
        'categorie': 'Viandes & Poissons',
        'unite_mesure': 'g',
        'lieu_rangement': 'Frigo (milieu)',
        'duree_conservation': 10,
        'mois_saison': None,
        'stock_limite': 150,
        'poids_estime_g': None
    },
    'Saumon': {
        'categorie': 'Viandes & Poissons',
        'unite_mesure': 'g',
        'lieu_rangement': 'Frigo (bas)',
        'duree_conservation': 2,
        'mois_saison': 'Janvier,Février,Mars,Avril,Mai,Juin,Septembre,Octobre,Novembre,Décembre',
        'stock_limite': 0,
        'poids_estime_g': None
    },
    'Veau (quasi)': {
        'categorie': 'Viandes & Poissons',
        'unite_mesure': 'g',
        'lieu_rangement': 'Frigo (bas)',
        'duree_conservation': 3,
        'mois_saison': None,
        'stock_limite': 0,
        'poids_estime_g': None
    },

    # Fruits & Légumes
    'Tomate grappe': {
        'categorie': 'Fruits & Légumes',
        'unite_mesure': 'pièce',
        'lieu_rangement': 'Corbeille à fruits',
        'duree_conservation': 5,
        'mois_saison': 'Mai,Juin,Juillet,Août,Septembre,Octobre',
        'stock_limite': 3,
        'poids_estime_g': 100
    },
    'Oignon': {
        'categorie': 'Fruits & Légumes',
        'unite_mesure': 'pièce',
        'lieu_rangement': 'Placard sec',
        'duree_conservation': 30,
        'mois_saison': None,
        'stock_limite': 3,
        'poids_estime_g': 150
    },
    'Oignon nouveau': {
        'categorie': 'Fruits & Légumes',
        'unite_mesure': 'pièce',
        'lieu_rangement': 'Frigo (bac à légumes)',
        'duree_conservation': 7,
        'mois_saison': 'Avril,Mai,Juin,Juillet',
        'stock_limite': 5,
        'poids_estime_g': 60
    },
    'Pomme de terre': {
        'categorie': 'Fruits & Légumes',
        'unite_mesure': 'g',
        'lieu_rangement': 'Cave',
        'duree_conservation': 60,
        'mois_saison': None,
        'stock_limite': 1000,
        'poids_estime_g': 150
    },
    'Carotte': {
        'categorie': 'Fruits & Légumes',
        'unite_mesure': 'pièce',
        'lieu_rangement': 'Frigo (bac à légumes)',
        'duree_conservation': 14,
        'mois_saison': None,
        'stock_limite': 5,
        'poids_estime_g': 100
    },
    'Navet': {
        'categorie': 'Fruits & Légumes',
        'unite_mesure': 'g',
        'lieu_rangement': 'Frigo (bac à légumes)',
        'duree_conservation': 14,
        'mois_saison': 'Janvier,Février,Mars,Avril,Octobre,Novembre,Décembre',
        'stock_limite': 300,
        'poids_estime_g': 150
    },
    'Chou de Bruxelles': {
        'categorie': 'Fruits & Légumes',
        'unite_mesure': 'g',
        'lieu_rangement': 'Frigo (bac à légumes)',
        'duree_conservation': 7,
        'mois_saison': 'Octobre,Novembre,Décembre,Janvier,Février',
        'stock_limite': 300,
        'poids_estime_g': None
    },
    'Poireau': {
        'categorie': 'Fruits & Légumes',
        'unite_mesure': 'pièce',
        'lieu_rangement': 'Frigo (bac à légumes)',
        'duree_conservation': 10,
        'mois_saison': 'Janvier,Février,Mars,Septembre,Octobre,Novembre,Décembre',
        'stock_limite': 2,
        'poids_estime_g': 200
    },
    'Citron': {
        'categorie': 'Fruits & Légumes',
        'unite_mesure': 'pièce',
        'lieu_rangement': 'Corbeille à fruits',
        'duree_conservation': 14,
        'mois_saison': 'Janvier,Février,Novembre,Décembre',
        'stock_limite': 2,
        'poids_estime_g': 100
    },
    'Fenouil': {
        'categorie': 'Fruits & Légumes',
        'unite_mesure': 'pièce',
        'lieu_rangement': 'Frigo (bac à légumes)',
        'duree_conservation': 7,
        'mois_saison': 'Mai,Juin,Juillet,Août,Septembre,Octobre',
        'stock_limite': 1,
        'poids_estime_g': 300
    },
    'Céleri (branche)': {
        'categorie': 'Fruits & Légumes',
        'unite_mesure': 'pièce',
        'lieu_rangement': 'Frigo (bac à légumes)',
        'duree_conservation': 7,
        'mois_saison': 'Juin,Juillet,Août,Septembre,Octobre,Novembre',
        'stock_limite': 1,
        'poids_estime_g': 80
    },

    # Herbes & Épices
    'Basilic': {
        'categorie': 'Herbes & Épices',
        'unite_mesure': 'bouquet',
        'lieu_rangement': 'Frigo (bac à légumes)',
        'duree_conservation': 3,
        'mois_saison': 'Mai,Juin,Juillet,Août,Septembre',
        'stock_limite': 0,
        'poids_estime_g': 30
    },
    'Ail': {
        'categorie': 'Fruits & Légumes',
        'unite_mesure': 'gousses',
        'lieu_rangement': 'Placard sec',
        'duree_conservation': 90,
        'mois_saison': None,
        'stock_limite': 10,
        'poids_estime_g': 5
    },
    'Laurier': {
        'categorie': 'Herbes & Épices',
        'unite_mesure': 'feuille',
        'lieu_rangement': 'Placard épices',
        'duree_conservation': 365,
        'mois_saison': None,
        'stock_limite': 5,
        'poids_estime_g': 1
    },
    'Thym': {
        'categorie': 'Herbes & Épices',
        'unite_mesure': 'branches',
        'lieu_rangement': 'Frigo (bac à légumes)',
        'duree_conservation': 7,
        'mois_saison': None,
        'stock_limite': 0,
        'poids_estime_g': 5
    },
    'Bouquet garni': {
        'categorie': 'Herbes & Épices',
        'unite_mesure': 'pièce',
        'lieu_rangement': 'Placard épices',
        'duree_conservation': 180,
        'mois_saison': None,
        'stock_limite': 1,
        'poids_estime_g': 10
    },
    'Muscade': {
        'categorie': 'Herbes & Épices',
        'unite_mesure': 'pincées',
        'lieu_rangement': 'Placard épices',
        'duree_conservation': 365,
        'mois_saison': None,
        'stock_limite': 0,
        'poids_estime_g': 0.5
    },
    'Poivre': {
        'categorie': 'Herbes & Épices',
        'unite_mesure': 'pincée',
        'lieu_rangement': 'Placard épices',
        'duree_conservation': 730,
        'mois_saison': None,
        'stock_limite': 10,
        'poids_estime_g': 0.5
    },
    'Piment d\'Espelette': {
        'categorie': 'Herbes & Épices',
        'unite_mesure': 'pincée',
        'lieu_rangement': 'Placard épices',
        'duree_conservation': 365,
        'mois_saison': None,
        'stock_limite': 5,
        'poids_estime_g': 0.5
    },
    'Gros sel': {
        'categorie': 'Épicerie salée',
        'unite_mesure': 'pincée',
        'lieu_rangement': 'Placard sec',
        'duree_conservation': 3650,
        'mois_saison': None,
        'stock_limite': 500,
        'poids_estime_g': 5
    },
    'Sel': {
        'categorie': 'Épicerie salée',
        'unite_mesure': 'pincée',
        'lieu_rangement': 'Placard sec',
        'duree_conservation': 3650,
        'mois_saison': None,
        'stock_limite': 500,
        'poids_estime_g': 5
    },
    'Fleur de sel': {
        'categorie': 'Épicerie salée',
        'unite_mesure': 'pincée',
        'lieu_rangement': 'Placard sec',
        'duree_conservation': 3650,
        'mois_saison': None,
        'stock_limite': 50,
        'poids_estime_g': 1
    },

    # Produits laitiers
    'Beurre': {
        'categorie': 'Produits laitiers',
        'unite_mesure': 'g',
        'lieu_rangement': 'Frigo (porte)',
        'duree_conservation': 30,
        'mois_saison': None,
        'stock_limite': 250,
        'poids_estime_g': None
    },
    'Crème fraîche': {
        'categorie': 'Produits laitiers',
        'unite_mesure': 'cl',
        'lieu_rangement': 'Frigo (haut)',
        'duree_conservation': 14,
        'mois_saison': None,
        'stock_limite': 20,
        'poids_estime_g': None
    },
    'Lait': {
        'categorie': 'Produits laitiers',
        'unite_mesure': 'cl',
        'lieu_rangement': 'Frigo (porte)',
        'duree_conservation': 7,
        'mois_saison': None,
        'stock_limite': 100,
        'poids_estime_g': None
    },

    # Boissons & Liquides
    'Vin blanc sec': {
        'categorie': 'Boissons',
        'unite_mesure': 'cl',
        'lieu_rangement': 'Cave',
        'duree_conservation': 365,
        'mois_saison': None,
        'stock_limite': 75,
        'poids_estime_g': None
    },
    'Bouillon de légumes': {
        'categorie': 'Épicerie salée',
        'unite_mesure': 'cl',
        'lieu_rangement': 'Placard sec',
        'duree_conservation': 180,
        'mois_saison': None,
        'stock_limite': 100,
        'poids_estime_g': None
    },
    'Fumet de poisson': {
        'categorie': 'Épicerie salée',
        'unite_mesure': 'cl',
        'lieu_rangement': 'Placard sec',
        'duree_conservation': 180,
        'mois_saison': None,
        'stock_limite': 50,
        'poids_estime_g': None
    },
    'Vinaigre blanc': {
        'categorie': 'Huiles & Vinaigres',
        'unite_mesure': 'cl',
        'lieu_rangement': 'Placard sec',
        'duree_conservation': 730,
        'mois_saison': None,
        'stock_limite': 50,
        'poids_estime_g': None
    },

    # Huiles
    'Huile d\'olive': {
        'categorie': 'Huiles & Vinaigres',
        'unite_mesure': 'CaS',
        'lieu_rangement': 'Placard sec',
        'duree_conservation': 365,
        'mois_saison': None,
        'stock_limite': 20,
        'poids_estime_g': 15  # 1 CaS = ~15ml
    },

    # Épicerie
    'Sucre en poudre': {
        'categorie': 'Épicerie sucrée',
        'unite_mesure': 'CaC',
        'lieu_rangement': 'Placard sec',
        'duree_conservation': 730,
        'mois_saison': None,
        'stock_limite': 500,
        'poids_estime_g': 5  # 1 CaC = ~5g
    },
    'Farine': {
        'categorie': 'Pâtes & Riz',
        'unite_mesure': 'CaS',
        'lieu_rangement': 'Placard sec',
        'duree_conservation': 180,
        'mois_saison': None,
        'stock_limite': 500,
        'poids_estime_g': 10  # 1 CaS = ~10g
    },
    'Bicarbonate de sodium': {
        'categorie': 'Épicerie salée',
        'unite_mesure': 'CaC',
        'lieu_rangement': 'Placard sec',
        'duree_conservation': 730,
        'mois_saison': None,
        'stock_limite': 50,
        'poids_estime_g': 5
    },
}

# Mise à jour des ingrédients
print("🔄 Mise à jour des ingrédients existants...\n")

for nom_ingredient, data in INGREDIENTS_DATA.items():
    ingredient = Ingredient.query.filter_by(nom=nom_ingredient).first()

    if ingredient:
        print(f"📝 Mise à jour : {nom_ingredient}")

        # Mettre à jour tous les champs
        ingredient.categorie = data['categorie']
        ingredient.unite_mesure = data['unite_mesure']
        ingredient.lieu_rangement = data['lieu_rangement']
        ingredient.duree_conservation = data['duree_conservation']
        ingredient.mois_saison = data['mois_saison']
        ingredient.stock_limite = data['stock_limite']
        ingredient.poids_estime_g = data['poids_estime_g']

        # Afficher les mois de saison si présents
        if data['mois_saison']:
            mois = data['mois_saison'].replace(',', ', ')
            print(f"   🌱 Saison: {mois}")

        print(f"   📍 Rangement: {data['lieu_rangement']}")
        print(f"   ⏱️  Conservation: {data['duree_conservation']} jours")
        if data['poids_estime_g']:
            print(f"   ⚖️  Poids estimé: {data['poids_estime_g']}g")
        print()
    else:
        print(f"⚠️  Ingrédient non trouvé : {nom_ingredient}")

db.session.commit()

print("="*50)
print("✅ Mise à jour terminée !")
print("="*50)
