"""
Script pour remplir la base de données avec des ingrédients de base
"""
from app import create_app, db
from app.models import Ingredient

# Liste complète d'ingrédients de base avec leurs informations
INGREDIENTS_BASE = [
    # Fruits & Légumes
    {'nom': 'Pomme de terre', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'kg', 'duree_conservation': 30},
    {'nom': 'Carotte', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'kg', 'duree_conservation': 14},
    {'nom': 'Oignon', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'kg', 'duree_conservation': 30},
    {'nom': 'Tomate', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'kg', 'duree_conservation': 7},
    {'nom': 'Courgette', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'kg', 'duree_conservation': 7},
    {'nom': 'Poivron', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'pièce', 'duree_conservation': 7},
    {'nom': 'Salade verte', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'pièce', 'duree_conservation': 5},
    {'nom': 'Ail', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'tête', 'duree_conservation': 30},
    {'nom': 'Échalote', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'kg', 'duree_conservation': 21},
    {'nom': 'Poireau', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'kg', 'duree_conservation': 7},
    {'nom': 'Champignon de Paris', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'g', 'duree_conservation': 3},
    {'nom': 'Brocoli', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'pièce', 'duree_conservation': 5},
    {'nom': 'Chou-fleur', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'pièce', 'duree_conservation': 7},
    {'nom': 'Épinard', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'g', 'duree_conservation': 3},
    {'nom': 'Haricot vert', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'g', 'duree_conservation': 5},
    {'nom': 'Banane', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'kg', 'duree_conservation': 5},
    {'nom': 'Pomme', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'kg', 'duree_conservation': 14},
    {'nom': 'Orange', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'kg', 'duree_conservation': 10},
    {'nom': 'Citron', 'categorie': 'Fruits & Légumes', 'unite_mesure': 'pièce', 'duree_conservation': 14},

    # Viandes & Poissons
    {'nom': 'Poulet', 'categorie': 'Viandes & Poissons', 'unite_mesure': 'kg', 'duree_conservation': 2},
    {'nom': 'Bœuf (steak)', 'categorie': 'Viandes & Poissons', 'unite_mesure': 'kg', 'duree_conservation': 3},
    {'nom': 'Porc', 'categorie': 'Viandes & Poissons', 'unite_mesure': 'kg', 'duree_conservation': 3},
    {'nom': 'Saumon', 'categorie': 'Viandes & Poissons', 'unite_mesure': 'kg', 'duree_conservation': 2},
    {'nom': 'Cabillaud', 'categorie': 'Viandes & Poissons', 'unite_mesure': 'kg', 'duree_conservation': 2},
    {'nom': 'Jambon blanc', 'categorie': 'Viandes & Poissons', 'unite_mesure': 'g', 'duree_conservation': 4},
    {'nom': 'Lardons', 'categorie': 'Viandes & Poissons', 'unite_mesure': 'g', 'duree_conservation': 7},
    {'nom': 'Saucisse', 'categorie': 'Viandes & Poissons', 'unite_mesure': 'pièce', 'duree_conservation': 5},

    # Produits laitiers
    {'nom': 'Lait', 'categorie': 'Produits laitiers', 'unite_mesure': 'L', 'duree_conservation': 7},
    {'nom': 'Beurre', 'categorie': 'Produits laitiers', 'unite_mesure': 'g', 'duree_conservation': 30},
    {'nom': 'Crème fraîche', 'categorie': 'Produits laitiers', 'unite_mesure': 'ml', 'duree_conservation': 7},
    {'nom': 'Yaourt nature', 'categorie': 'Produits laitiers', 'unite_mesure': 'pièce', 'duree_conservation': 20},
    {'nom': 'Fromage râpé', 'categorie': 'Produits laitiers', 'unite_mesure': 'g', 'duree_conservation': 14},
    {'nom': 'Mozzarella', 'categorie': 'Produits laitiers', 'unite_mesure': 'g', 'duree_conservation': 7},
    {'nom': 'Parmesan', 'categorie': 'Produits laitiers', 'unite_mesure': 'g', 'duree_conservation': 30},
    {'nom': 'Fromage de chèvre', 'categorie': 'Produits laitiers', 'unite_mesure': 'g', 'duree_conservation': 14},
    {'nom': 'Œuf', 'categorie': 'Produits laitiers', 'unite_mesure': 'pièce', 'duree_conservation': 28},

    # Épicerie salée
    {'nom': 'Sel', 'categorie': 'Épicerie salée', 'unite_mesure': 'g', 'duree_conservation': 365},
    {'nom': 'Poivre', 'categorie': 'Épicerie salée', 'unite_mesure': 'g', 'duree_conservation': 365},
    {'nom': 'Farine', 'categorie': 'Épicerie salée', 'unite_mesure': 'g', 'duree_conservation': 180},
    {'nom': 'Bouillon cube', 'categorie': 'Épicerie salée', 'unite_mesure': 'pièce', 'duree_conservation': 365},
    {'nom': 'Levure chimique', 'categorie': 'Épicerie salée', 'unite_mesure': 'g', 'duree_conservation': 365},

    # Épicerie sucrée
    {'nom': 'Sucre', 'categorie': 'Épicerie sucrée', 'unite_mesure': 'g', 'duree_conservation': 365},
    {'nom': 'Chocolat noir', 'categorie': 'Épicerie sucrée', 'unite_mesure': 'g', 'duree_conservation': 180},
    {'nom': 'Miel', 'categorie': 'Épicerie sucrée', 'unite_mesure': 'g', 'duree_conservation': 365},
    {'nom': 'Confiture', 'categorie': 'Épicerie sucrée', 'unite_mesure': 'g', 'duree_conservation': 90},

    # Pâtes & Riz
    {'nom': 'Pâtes', 'categorie': 'Pâtes & Riz', 'unite_mesure': 'g', 'duree_conservation': 365},
    {'nom': 'Riz blanc', 'categorie': 'Pâtes & Riz', 'unite_mesure': 'g', 'duree_conservation': 365},
    {'nom': 'Riz basmati', 'categorie': 'Pâtes & Riz', 'unite_mesure': 'g', 'duree_conservation': 365},
    {'nom': 'Quinoa', 'categorie': 'Pâtes & Riz', 'unite_mesure': 'g', 'duree_conservation': 365},
    {'nom': 'Semoule', 'categorie': 'Pâtes & Riz', 'unite_mesure': 'g', 'duree_conservation': 365},

    # Conserves
    {'nom': 'Tomate pelée (conserve)', 'categorie': 'Conserves', 'unite_mesure': 'g', 'duree_conservation': 730},
    {'nom': 'Coulis de tomate', 'categorie': 'Conserves', 'unite_mesure': 'g', 'duree_conservation': 365},
    {'nom': 'Thon (conserve)', 'categorie': 'Conserves', 'unite_mesure': 'g', 'duree_conservation': 1095},
    {'nom': 'Maïs (conserve)', 'categorie': 'Conserves', 'unite_mesure': 'g', 'duree_conservation': 730},
    {'nom': 'Haricot rouge (conserve)', 'categorie': 'Conserves', 'unite_mesure': 'g', 'duree_conservation': 730},
    {'nom': 'Pois chiche (conserve)', 'categorie': 'Conserves', 'unite_mesure': 'g', 'duree_conservation': 730},

    # Condiments & Sauces
    {'nom': 'Huile d\'olive', 'categorie': 'Huiles & Vinaigres', 'unite_mesure': 'ml', 'duree_conservation': 365},
    {'nom': 'Huile de tournesol', 'categorie': 'Huiles & Vinaigres', 'unite_mesure': 'ml', 'duree_conservation': 365},
    {'nom': 'Vinaigre balsamique', 'categorie': 'Huiles & Vinaigres', 'unite_mesure': 'ml', 'duree_conservation': 365},
    {'nom': 'Vinaigre de vin', 'categorie': 'Huiles & Vinaigres', 'unite_mesure': 'ml', 'duree_conservation': 365},
    {'nom': 'Moutarde', 'categorie': 'Condiments & Sauces', 'unite_mesure': 'g', 'duree_conservation': 180},
    {'nom': 'Ketchup', 'categorie': 'Condiments & Sauces', 'unite_mesure': 'g', 'duree_conservation': 180},
    {'nom': 'Mayonnaise', 'categorie': 'Condiments & Sauces', 'unite_mesure': 'g', 'duree_conservation': 90},
    {'nom': 'Sauce soja', 'categorie': 'Condiments & Sauces', 'unite_mesure': 'ml', 'duree_conservation': 365},

    # Herbes & Épices
    {'nom': 'Basilic', 'categorie': 'Herbes & Épices', 'unite_mesure': 'g', 'duree_conservation': 3},
    {'nom': 'Persil', 'categorie': 'Herbes & Épices', 'unite_mesure': 'g', 'duree_conservation': 5},
    {'nom': 'Thym', 'categorie': 'Herbes & Épices', 'unite_mesure': 'g', 'duree_conservation': 180},
    {'nom': 'Laurier', 'categorie': 'Herbes & Épices', 'unite_mesure': 'feuille', 'duree_conservation': 365},
    {'nom': 'Origan', 'categorie': 'Herbes & Épices', 'unite_mesure': 'g', 'duree_conservation': 180},
    {'nom': 'Paprika', 'categorie': 'Herbes & Épices', 'unite_mesure': 'g', 'duree_conservation': 365},
    {'nom': 'Cumin', 'categorie': 'Herbes & Épices', 'unite_mesure': 'g', 'duree_conservation': 365},
    {'nom': 'Curry', 'categorie': 'Herbes & Épices', 'unite_mesure': 'g', 'duree_conservation': 365},
    {'nom': 'Gingembre', 'categorie': 'Herbes & Épices', 'unite_mesure': 'g', 'duree_conservation': 14},

    # Pain & Viennoiseries
    {'nom': 'Pain', 'categorie': 'Pain & Viennoiseries', 'unite_mesure': 'g', 'duree_conservation': 3},
    {'nom': 'Pain de mie', 'categorie': 'Pain & Viennoiseries', 'unite_mesure': 'tranche', 'duree_conservation': 7},

    # Surgelés
    {'nom': 'Petits pois surgelés', 'categorie': 'Surgelés', 'unite_mesure': 'g', 'duree_conservation': 365},
    {'nom': 'Haricot vert surgelé', 'categorie': 'Surgelés', 'unite_mesure': 'g', 'duree_conservation': 365},
    {'nom': 'Épinard surgelé', 'categorie': 'Surgelés', 'unite_mesure': 'g', 'duree_conservation': 365},

    # Boissons
    {'nom': 'Eau', 'categorie': 'Boissons', 'unite_mesure': 'L', 'duree_conservation': 365},
    {'nom': 'Jus d\'orange', 'categorie': 'Boissons', 'unite_mesure': 'L', 'duree_conservation': 7},
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
                    duree_conservation=ing_data['duree_conservation']
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
