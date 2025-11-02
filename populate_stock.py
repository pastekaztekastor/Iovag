"""
Script pour ajouter des données de test au stock
"""
from app import create_app, db
from app.models import User, Stock, Ingredient

def populate_stock():
    """Ajouter du stock de test pour le premier utilisateur"""
    app = create_app()

    with app.app_context():
        print("📦 Ajout de données de test au stock...")

        # Récupérer le premier utilisateur
        user = User.query.first()
        if not user:
            print("❌ Aucun utilisateur trouvé. Veuillez créer un utilisateur d'abord.")
            return

        print(f"✅ Utilisateur trouvé: {user.username}")

        # Vider le stock existant pour cet utilisateur
        Stock.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        print("🗑️  Stock existant supprimé")

        # Stocks de test - variété d'ingrédients avec différents niveaux
        stocks_test = [
            # Stock OK
            {'nom': 'Carotte', 'quantite': 500, 'unite': 'g'},
            {'nom': 'Pomme de terre', 'quantite': 2000, 'unite': 'g'},
            {'nom': 'Pâtes', 'quantite': 500, 'unite': 'g'},
            {'nom': 'Riz blanc', 'quantite': 1000, 'unite': 'g'},
            {'nom': 'Farine', 'quantite': 1000, 'unite': 'g'},
            {'nom': 'Sucre', 'quantite': 500, 'unite': 'g'},
            {'nom': "Huile d'olive", 'quantite': 500, 'unite': 'ml'},
            {'nom': 'Sel', 'quantite': 200, 'unite': 'g'},
            {'nom': 'Poivre', 'quantite': 50, 'unite': 'g'},
            {'nom': 'Œuf', 'quantite': 12, 'unite': 'pièce'},

            # Stock bas (devrait afficher des alertes)
            {'nom': 'Lait', 'quantite': 100, 'unite': 'ml'},  # Stock bas
            {'nom': 'Beurre', 'quantite': 50, 'unite': 'g'},  # Stock bas
            {'nom': 'Oignon', 'quantite': 2, 'unite': 'pièce'},
            {'nom': 'Ail', 'quantite': 3, 'unite': 'gousse'},
            {'nom': 'Tomate', 'quantite': 150, 'unite': 'g'},  # Stock bas
            {'nom': 'Basilic', 'quantite': 10, 'unite': 'g'},
            {'nom': 'Parmesan', 'quantite': 50, 'unite': 'g'},  # Stock bas
            {'nom': 'Crème fraîche', 'quantite': 80, 'unite': 'ml'},  # Stock bas

            # Quelques autres pour tester les lieux de rangement
            {'nom': 'Chocolat noir', 'quantite': 200, 'unite': 'g'},
            {'nom': 'Miel', 'quantite': 150, 'unite': 'g'},
            {'nom': 'Confiture', 'quantite': 100, 'unite': 'g'},
            {'nom': 'Moutarde', 'quantite': 120, 'unite': 'g'},
            {'nom': 'Thym', 'quantite': 15, 'unite': 'g'},
            {'nom': 'Laurier', 'quantite': 10, 'unite': 'g'},
        ]

        count_added = 0
        count_not_found = 0

        for stock_data in stocks_test:
            ingredient = Ingredient.query.filter_by(nom=stock_data['nom']).first()

            if ingredient:
                stock = Stock(
                    user_id=user.id,
                    ingredient_id=ingredient.id,
                    quantite=stock_data['quantite'],
                    unite=stock_data['unite']
                )
                db.session.add(stock)
                print(f"  ✅ Ajouté: {stock_data['nom']} - {stock_data['quantite']} {stock_data['unite']}")
                count_added += 1
            else:
                print(f"  ❌ Ingrédient non trouvé: {stock_data['nom']}")
                count_not_found += 1

        db.session.commit()

        print(f"\n📊 Résumé:")
        print(f"  ✅ {count_added} stocks ajoutés")
        print(f"  ❌ {count_not_found} ingrédients non trouvés")
        print("\n✨ Terminé! Vous pouvez maintenant tester la gestion de stock.")


if __name__ == '__main__':
    populate_stock()
