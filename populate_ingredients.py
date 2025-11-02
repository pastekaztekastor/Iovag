"""
Script pour remplir la base de données avec des ingrédients de base
"""
from app import create_app, db
from app.models import Ingredient

# Liste complète d'ingrédients de base avec leurs informations
INGREDIENTS_BASE = [
    # Fruits & Légumes
    {'nom': 'Pomme de terre', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'kg', 'duree_conservation': 30, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Carotte', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'kg', 'duree_conservation': 14, 'lieu_rangement': 'Frigo (bac à légumes)'},
    {'nom': 'Oignon', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'kg', 'duree_conservation': 30, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Tomate', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'kg', 'duree_conservation': 7, 'lieu_rangement': 'Corbeille à fruits'},
    {'nom': 'Courgette', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'kg', 'duree_conservation': 7, 'lieu_rangement': 'Frigo (bac à légumes)'},
    {'nom': 'Poivron', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'pièce', 'duree_conservation': 7, 'lieu_rangement': 'Frigo (bac à légumes)'},
    {'nom': 'Salade verte', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'pièce', 'duree_conservation': 5, 'lieu_rangement': 'Frigo (bac à légumes)'},
    {'nom': 'Ail', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'tête', 'duree_conservation': 30, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Échalote', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'kg', 'duree_conservation': 21, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Poireau', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'kg', 'duree_conservation': 7, 'lieu_rangement': 'Frigo (bac à légumes)'},
    {'nom': 'Champignon de Paris', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'g', 'duree_conservation': 3, 'lieu_rangement': 'Frigo (bas)'},
    {'nom': 'Brocoli', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'pièce', 'duree_conservation': 5, 'lieu_rangement': 'Frigo (bac à légumes)'},
    {'nom': 'Chou-fleur', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'pièce', 'duree_conservation': 7, 'lieu_rangement': 'Frigo (bac à légumes)'},
    {'nom': 'Épinard', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'g', 'duree_conservation': 3, 'lieu_rangement': 'Frigo (bac à légumes)'},
    {'nom': 'Haricot vert', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'g', 'duree_conservation': 5, 'lieu_rangement': 'Frigo (bac à légumes)'},
    {'nom': 'Banane', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'kg', 'duree_conservation': 5, 'lieu_rangement': 'Corbeille à fruits'},
    {'nom': 'Pomme', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'kg', 'duree_conservation': 14, 'lieu_rangement': 'Corbeille à fruits'},
    {'nom': 'Orange', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'kg', 'duree_conservation': 10, 'lieu_rangement': 'Corbeille à fruits'},
    {'nom': 'Citron', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'pièce', 'duree_conservation': 14, 'lieu_rangement': 'Frigo (porte)'},

    # Viandes & Poissons
    {'nom': 'Poulet', 'categorie': 'Viandes & Poissons', 'unite_mesure': 'kg', 'duree_conservation': 2, 'lieu_rangement': 'Frigo (bas)'},
    {'nom': 'Bœuf (steak)', 'categorie': 'Viandes & Poissons', 'unite_mesure': 'kg', 'duree_conservation': 3, 'lieu_rangement': 'Frigo (bas)'},
    {'nom': 'Porc', 'categorie': 'Viandes & Poissons', 'unite_mesure': 'kg', 'duree_conservation': 3, 'lieu_rangement': 'Frigo (bas)'},
    {'nom': 'Saumon', 'categorie': 'Viandes & Poissons', 'unite_mesure': 'kg', 'duree_conservation': 2, 'lieu_rangement': 'Frigo (bas)'},
    {'nom': 'Cabillaud', 'categorie': 'Viandes & Poissons', 'unite_mesure': 'kg', 'duree_conservation': 2, 'lieu_rangement': 'Frigo (bas)'},
    {'nom': 'Jambon blanc', 'categorie': 'Viandes & Poissons', 'unite_mesure': 'g', 'duree_conservation': 4, 'lieu_rangement': 'Frigo (milieu)'},
    {'nom': 'Lardons', 'categorie': 'Viandes & Poissons', 'unite_mesure': 'g', 'duree_conservation': 7, 'lieu_rangement': 'Frigo (milieu)'},
    {'nom': 'Saucisse', 'categorie': 'Viandes & Poissons', 'unite_mesure': 'pièce', 'duree_conservation': 5, 'lieu_rangement': 'Frigo (bas)'},

    # Produits laitiers
    {'nom': 'Lait', 'categorie': 'Produits laitiers', 'unite_mesure': 'L', 'duree_conservation': 7, 'lieu_rangement': 'Frigo (porte)'},
    {'nom': 'Beurre', 'categorie': 'Produits laitiers', 'unite_mesure': 'g', 'duree_conservation': 30, 'lieu_rangement': 'Frigo (porte)'},
    {'nom': 'Crème fraîche', 'categorie': 'Produits laitiers', 'unite_mesure': 'ml', 'duree_conservation': 7, 'lieu_rangement': 'Frigo (haut)'},
    {'nom': 'Yaourt nature', 'categorie': 'Produits laitiers', 'unite_mesure': 'pièce', 'duree_conservation': 20, 'lieu_rangement': 'Frigo (haut)'},
    {'nom': 'Fromage râpé', 'categorie': 'Produits laitiers', 'unite_mesure': 'g', 'duree_conservation': 14, 'lieu_rangement': 'Frigo (milieu)'},
    {'nom': 'Mozzarella', 'categorie': 'Produits laitiers', 'unite_mesure': 'g', 'duree_conservation': 7, 'lieu_rangement': 'Frigo (milieu)'},
    {'nom': 'Parmesan', 'categorie': 'Produits laitiers', 'unite_mesure': 'g', 'duree_conservation': 30, 'lieu_rangement': 'Frigo (milieu)'},
    {'nom': 'Fromage de chèvre', 'categorie': 'Produits laitiers', 'unite_mesure': 'g', 'duree_conservation': 14, 'lieu_rangement': 'Frigo (milieu)'},
    {'nom': 'Œuf', 'categorie': 'Produits laitiers', 'unite_mesure': 'pièce', 'duree_conservation': 28, 'lieu_rangement': 'Frigo (porte)'},

    # Épicerie salée
    {'nom': 'Sel', 'categorie': 'Épicerie salée', 'unite_mesure': 'g', 'duree_conservation': 365, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Poivre', 'categorie': 'Épicerie salée', 'unite_mesure': 'g', 'duree_conservation': 365, 'lieu_rangement': 'Placard épices'},
    {'nom': 'Farine', 'categorie': 'Épicerie salée', 'unite_mesure': 'g', 'duree_conservation': 180, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Bouillon cube', 'categorie': 'Épicerie salée', 'unite_mesure': 'pièce', 'duree_conservation': 365, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Levure chimique', 'categorie': 'Épicerie salée', 'unite_mesure': 'g', 'duree_conservation': 365, 'lieu_rangement': 'Placard sec'},

    # Épicerie sucrée
    {'nom': 'Sucre', 'categorie': 'Épicerie sucrée', 'unite_mesure': 'g', 'duree_conservation': 365, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Chocolat noir', 'categorie': 'Épicerie sucrée', 'unite_mesure': 'g', 'duree_conservation': 180, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Miel', 'categorie': 'Épicerie sucrée', 'unite_mesure': 'g', 'duree_conservation': 365, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Confiture', 'categorie': 'Épicerie sucrée', 'unite_mesure': 'g', 'duree_conservation': 90, 'lieu_rangement': 'Frigo (porte)'},

    # Pâtes & Riz
    {'nom': 'Pâtes', 'categorie': 'Pâtes & Riz', 'unite_mesure': 'g', 'duree_conservation': 365, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Riz blanc', 'categorie': 'Pâtes & Riz', 'unite_mesure': 'g', 'duree_conservation': 365, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Riz basmati', 'categorie': 'Pâtes & Riz', 'unite_mesure': 'g', 'duree_conservation': 365, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Quinoa', 'categorie': 'Pâtes & Riz', 'unite_mesure': 'g', 'duree_conservation': 365, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Semoule', 'categorie': 'Pâtes & Riz', 'unite_mesure': 'g', 'duree_conservation': 365, 'lieu_rangement': 'Placard sec'},

    # Conserves
    {'nom': 'Tomate pelée (conserve)', 'categorie': 'Conserves', 'unite_mesure': 'g', 'duree_conservation': 730, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Coulis de tomate', 'categorie': 'Conserves', 'unite_mesure': 'g', 'duree_conservation': 365, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Thon (conserve)', 'categorie': 'Conserves', 'unite_mesure': 'g', 'duree_conservation': 1095, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Maïs (conserve)', 'categorie': 'Conserves', 'unite_mesure': 'g', 'duree_conservation': 730, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Haricot rouge (conserve)', 'categorie': 'Conserves', 'unite_mesure': 'g', 'duree_conservation': 730, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Pois chiche (conserve)', 'categorie': 'Conserves', 'unite_mesure': 'g', 'duree_conservation': 730, 'lieu_rangement': 'Placard sec'},

    # Condiments & Sauces
    {'nom': 'Huile d\'olive', 'categorie': 'Huiles & Vinaigres', 'unite_mesure': 'ml', 'duree_conservation': 365, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Huile de tournesol', 'categorie': 'Huiles & Vinaigres', 'unite_mesure': 'ml', 'duree_conservation': 365, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Vinaigre balsamique', 'categorie': 'Huiles & Vinaigres', 'unite_mesure': 'ml', 'duree_conservation': 365, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Vinaigre de vin', 'categorie': 'Huiles & Vinaigres', 'unite_mesure': 'ml', 'duree_conservation': 365, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Moutarde', 'categorie': 'Condiments & Sauces', 'unite_mesure': 'g', 'duree_conservation': 180, 'lieu_rangement': 'Frigo (porte)'},
    {'nom': 'Ketchup', 'categorie': 'Condiments & Sauces', 'unite_mesure': 'g', 'duree_conservation': 180, 'lieu_rangement': 'Frigo (porte)'},
    {'nom': 'Mayonnaise', 'categorie': 'Condiments & Sauces', 'unite_mesure': 'g', 'duree_conservation': 90, 'lieu_rangement': 'Frigo (porte)'},
    {'nom': 'Sauce soja', 'categorie': 'Condiments & Sauces', 'unite_mesure': 'ml', 'duree_conservation': 365, 'lieu_rangement': 'Placard sec'},

    # Herbes & Épices
    {'nom': 'Basilic', 'categorie': 'Herbes & Épices', 'unite_mesure': 'g', 'duree_conservation': 3, 'lieu_rangement': 'Frigo (bac à légumes)'},
    {'nom': 'Persil', 'categorie': 'Herbes & Épices', 'unite_mesure': 'g', 'duree_conservation': 5, 'lieu_rangement': 'Frigo (bac à légumes)'},
    {'nom': 'Thym', 'categorie': 'Herbes & Épices', 'unite_mesure': 'g', 'duree_conservation': 180, 'lieu_rangement': 'Placard épices'},
    {'nom': 'Laurier', 'categorie': 'Herbes & Épices', 'unite_mesure': 'feuille', 'duree_conservation': 365, 'lieu_rangement': 'Placard épices'},
    {'nom': 'Origan', 'categorie': 'Herbes & Épices', 'unite_mesure': 'g', 'duree_conservation': 180, 'lieu_rangement': 'Placard épices'},
    {'nom': 'Paprika', 'categorie': 'Herbes & Épices', 'unite_mesure': 'g', 'duree_conservation': 365, 'lieu_rangement': 'Placard épices'},
    {'nom': 'Cumin', 'categorie': 'Herbes & Épices', 'unite_mesure': 'g', 'duree_conservation': 365, 'lieu_rangement': 'Placard épices'},
    {'nom': 'Curry', 'categorie': 'Herbes & Épices', 'unite_mesure': 'g', 'duree_conservation': 365, 'lieu_rangement': 'Placard épices'},
    {'nom': 'Gingembre', 'categorie': 'Herbes & Épices', 'unite_mesure': 'g', 'duree_conservation': 14, 'lieu_rangement': 'Frigo (bac à légumes)'},

    # Pain & Viennoiseries
    {'nom': 'Pain', 'categorie': 'Pain & Viennoiseries', 'unite_mesure': 'g', 'duree_conservation': 3, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Pain de mie', 'categorie': 'Pain & Viennoiseries', 'unite_mesure': 'tranche', 'duree_conservation': 7, 'lieu_rangement': 'Placard sec'},

    # Surgelés
    {'nom': 'Petits pois surgelés', 'categorie': 'Surgelés', 'unite_mesure': 'g', 'duree_conservation': 365, 'lieu_rangement': 'Congélateur'},
    {'nom': 'Haricot vert surgelé', 'categorie': 'Surgelés', 'unite_mesure': 'g', 'duree_conservation': 365, 'lieu_rangement': 'Congélateur'},
    {'nom': 'Épinard surgelé', 'categorie': 'Surgelés', 'unite_mesure': 'g', 'duree_conservation': 365, 'lieu_rangement': 'Congélateur'},

    # Boissons
    {'nom': 'Eau', 'categorie': 'Boissons', 'unite_mesure': 'L', 'duree_conservation': 365, 'lieu_rangement': 'Placard sec'},
    {'nom': 'Jus d\'orange', 'categorie': 'Boissons', 'unite_mesure': 'L', 'duree_conservation': 7, 'lieu_rangement': 'Frigo (porte)'},
]


def populate_ingredients():
    """Remplir la base avec les ingrédients de base"""
    app = create_app()

    with app.app_context():
        print("🍳 Début du remplissage de la base d'ingrédients...")

        count_added = 0
        count_skipped = 0

        for ing_data in INGREDIENTS_BASE:
            # Vérifier si l'ingrédient existe déjà
            existing = Ingredient.query.filter_by(nom=ing_data['nom']).first()

            if existing:
                print(f"  ⏭️  '{ing_data['nom']}' existe déjà")
                count_skipped += 1
            else:
                ingredient = Ingredient(
                    nom=ing_data['nom'],
                    categorie=ing_data['categorie'],
                    unite_mesure=ing_data['unite_mesure'],
                    duree_conservation=ing_data['duree_conservation'],
                    lieu_rangement=ing_data.get('lieu_rangement')
                )
                db.session.add(ingredient)
                print(f"  ✅ Ajouté: {ing_data['nom']} ({ing_data['categorie']})")
                count_added += 1

        db.session.commit()

        print(f"\n📊 Résumé:")
        print(f"  ✅ {count_added} ingrédients ajoutés")
        print(f"  ⏭️  {count_skipped} ingrédients déjà présents")
        print(f"  📦 Total dans la base: {Ingredient.query.count()}")
        print("\n✨ Terminé!")


if __name__ == '__main__':
    populate_ingredients()
