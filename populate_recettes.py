"""
Script pour ajouter des recettes de base
"""
from app import create_app, db
from app.models import User, Recette, Ingredient, RecetteIngredient, Instruction

RECETTES_BASE = [
    {
        'nom': 'Pâtes Carbonara',
        'portions': 4,
        'temps_preparation': '10 min',
        'temps_cuisson': '15 min',
        'auteur_nom': 'Cuisine italienne',
        'evaluation': 5,
        'note': 'Un grand classique italien, simple et délicieux',
        'ingredients': [
            {'nom': 'Pâtes', 'quantite': 400, 'unite': 'g'},
            {'nom': 'Lardons', 'quantite': 200, 'unite': 'g'},
            {'nom': 'Œuf', 'quantite': 4, 'unite': 'pièce'},
            {'nom': 'Parmesan', 'quantite': 100, 'unite': 'g'},
            {'nom': 'Crème fraîche', 'quantite': 200, 'unite': 'ml'},
            {'nom': 'Sel', 'quantite': 5, 'unite': 'g'},
            {'nom': 'Poivre', 'quantite': 2, 'unite': 'g'},
        ],
        'instructions': [
            'Faire cuire les pâtes dans une grande casserole d\'eau salée',
            'Faire revenir les lardons dans une poêle sans matière grasse',
            'Dans un bol, mélanger les œufs, la crème fraîche et le parmesan râpé',
            'Égoutter les pâtes et les ajouter aux lardons',
            'Retirer du feu et ajouter le mélange œufs-crème, mélanger rapidement',
            'Poivrer généreusement et servir immédiatement'
        ]
    },
    {
        'nom': 'Omelette aux fines herbes',
        'portions': 2,
        'temps_preparation': '5 min',
        'temps_cuisson': '5 min',
        'auteur_nom': 'Cuisine française',
        'evaluation': 4,
        'note': 'Parfait pour un repas rapide',
        'ingredients': [
            {'nom': 'Œuf', 'quantite': 6, 'unite': 'pièce'},
            {'nom': 'Beurre', 'quantite': 30, 'unite': 'g'},
            {'nom': 'Persil', 'quantite': 10, 'unite': 'g'},
            {'nom': 'Sel', 'quantite': 3, 'unite': 'g'},
            {'nom': 'Poivre', 'quantite': 2, 'unite': 'g'},
        ],
        'instructions': [
            'Battre les œufs dans un bol avec sel et poivre',
            'Hacher finement le persil et l\'ajouter aux œufs',
            'Faire fondre le beurre dans une poêle',
            'Verser les œufs et laisser cuire à feu moyen',
            'Quand les bords sont pris, replier l\'omelette en deux',
            'Servir immédiatement'
        ]
    },
    {
        'nom': 'Poulet rôti aux herbes',
        'portions': 4,
        'temps_preparation': '15 min',
        'temps_cuisson': '1h15',
        'auteur_nom': 'Cuisine traditionnelle',
        'evaluation': 5,
        'note': 'Le grand classique du dimanche',
        'ingredients': [
            {'nom': 'Poulet', 'quantite': 1500, 'unite': 'g'},
            {'nom': 'Beurre', 'quantite': 50, 'unite': 'g'},
            {'nom': 'Thym', 'quantite': 5, 'unite': 'g'},
            {'nom': 'Laurier', 'quantite': 3, 'unite': 'feuille'},
            {'nom': 'Ail', 'quantite': 4, 'unite': 'gousse'},
            {'nom': 'Sel', 'quantite': 10, 'unite': 'g'},
            {'nom': 'Poivre', 'quantite': 5, 'unite': 'g'},
        ],
        'instructions': [
            'Préchauffer le four à 200°C',
            'Frotter le poulet avec du beurre, du sel et du poivre',
            'Placer le thym, le laurier et l\'ail dans le poulet',
            'Mettre le poulet dans un plat allant au four',
            'Enfourner pendant 1h15, arroser régulièrement',
            'Vérifier la cuisson en piquant la cuisse (le jus doit être clair)',
            'Laisser reposer 10 minutes avant de découper'
        ]
    },
    {
        'nom': 'Quiche lorraine',
        'portions': 6,
        'temps_preparation': '20 min',
        'temps_cuisson': '35 min',
        'auteur_nom': 'Cuisine lorraine',
        'evaluation': 5,
        'note': 'La vraie recette traditionnelle',
        'ingredients': [
            {'nom': 'Pâte brisée', 'quantite': 1, 'unite': 'pièce'},
            {'nom': 'Lardons', 'quantite': 200, 'unite': 'g'},
            {'nom': 'Œuf', 'quantite': 4, 'unite': 'pièce'},
            {'nom': 'Crème fraîche', 'quantite': 300, 'unite': 'ml'},
            {'nom': 'Lait', 'quantite': 100, 'unite': 'ml'},
            {'nom': 'Fromage râpé', 'quantite': 100, 'unite': 'g'},
            {'nom': 'Muscade', 'quantite': 2, 'unite': 'g'},
            {'nom': 'Sel', 'quantite': 5, 'unite': 'g'},
            {'nom': 'Poivre', 'quantite': 3, 'unite': 'g'},
        ],
        'instructions': [
            'Préchauffer le four à 180°C',
            'Étaler la pâte dans un moule à tarte',
            'Faire revenir les lardons sans matière grasse',
            'Battre les œufs avec la crème et le lait',
            'Ajouter sel, poivre et muscade',
            'Disposer les lardons sur la pâte',
            'Verser l\'appareil à quiche et parsemer de fromage',
            'Enfourner 35 minutes jusqu\'à ce que la quiche soit dorée'
        ]
    },
    {
        'nom': 'Gratin dauphinois',
        'portions': 6,
        'temps_preparation': '20 min',
        'temps_cuisson': '1h',
        'auteur_nom': 'Cuisine dauphinoise',
        'evaluation': 5,
        'note': 'Sans fromage pour la vraie recette!',
        'ingredients': [
            {'nom': 'Pomme de terre', 'quantite': 1500, 'unite': 'g'},
            {'nom': 'Crème fraîche', 'quantite': 400, 'unite': 'ml'},
            {'nom': 'Lait', 'quantite': 200, 'unite': 'ml'},
            {'nom': 'Ail', 'quantite': 2, 'unite': 'gousse'},
            {'nom': 'Beurre', 'quantite': 30, 'unite': 'g'},
            {'nom': 'Muscade', 'quantite': 2, 'unite': 'g'},
            {'nom': 'Sel', 'quantite': 8, 'unite': 'g'},
            {'nom': 'Poivre', 'quantite': 3, 'unite': 'g'},
        ],
        'instructions': [
            'Préchauffer le four à 160°C',
            'Éplucher et couper les pommes de terre en fines rondelles',
            'Frotter un plat avec l\'ail et le beurrer',
            'Disposer les pommes de terre en couches',
            'Mélanger la crème et le lait avec sel, poivre et muscade',
            'Verser sur les pommes de terre',
            'Enfourner 1h jusqu\'à ce que le dessus soit doré'
        ]
    },
    {
        'nom': 'Salade César',
        'portions': 4,
        'temps_preparation': '15 min',
        'temps_cuisson': '10 min',
        'auteur_nom': 'Cuisine américaine',
        'evaluation': 4,
        'note': 'Fraîche et copieuse',
        'ingredients': [
            {'nom': 'Salade romaine', 'quantite': 2, 'unite': 'pièce'},
            {'nom': 'Poulet', 'quantite': 400, 'unite': 'g'},
            {'nom': 'Parmesan', 'quantite': 80, 'unite': 'g'},
            {'nom': 'Pain', 'quantite': 100, 'unite': 'g'},
            {'nom': 'Œuf', 'quantite': 2, 'unite': 'pièce'},
            {'nom': 'Ail', 'quantite': 1, 'unite': 'gousse'},
            {'nom': 'Moutarde', 'quantite': 15, 'unite': 'g'},
            {'nom': "Huile d'olive", 'quantite': 100, 'unite': 'ml'},
            {'nom': 'Citron', 'quantite': 1, 'unite': 'pièce'},
        ],
        'instructions': [
            'Faire cuire le poulet et le couper en lamelles',
            'Préparer des croûtons avec le pain',
            'Laver et couper la salade',
            'Préparer la sauce: mélanger œuf, moutarde, ail, jus de citron',
            'Ajouter l\'huile en filet en fouettant',
            'Mélanger la salade avec la sauce',
            'Ajouter le poulet, les croûtons et le parmesan râpé'
        ]
    },
    {
        'nom': 'Risotto aux champignons',
        'portions': 4,
        'temps_preparation': '15 min',
        'temps_cuisson': '25 min',
        'auteur_nom': 'Cuisine italienne',
        'evaluation': 5,
        'note': 'Crémeux et parfumé',
        'ingredients': [
            {'nom': 'Riz arborio', 'quantite': 300, 'unite': 'g'},
            {'nom': 'Champignon de Paris', 'quantite': 400, 'unite': 'g'},
            {'nom': 'Oignon', 'quantite': 1, 'unite': 'pièce'},
            {'nom': 'Parmesan', 'quantite': 80, 'unite': 'g'},
            {'nom': 'Beurre', 'quantite': 60, 'unite': 'g'},
            {'nom': 'Vin blanc', 'quantite': 150, 'unite': 'ml'},
            {'nom': 'Bouillon de volaille', 'quantite': 1, 'unite': 'l'},
            {'nom': "Huile d'olive", 'quantite': 30, 'unite': 'ml'},
        ],
        'instructions': [
            'Émincer l\'oignon et faire revenir dans l\'huile',
            'Ajouter le riz et nacrer pendant 2 minutes',
            'Verser le vin blanc et laisser évaporer',
            'Ajouter le bouillon louche par louche en remuant',
            'Faire revenir les champignons dans une poêle',
            'Ajouter les champignons au riz en fin de cuisson',
            'Hors du feu, ajouter beurre et parmesan, mélanger'
        ]
    },
    {
        'nom': 'Crêpes sucrées',
        'portions': 4,
        'temps_preparation': '10 min',
        'temps_cuisson': '20 min',
        'auteur_nom': 'Cuisine bretonne',
        'evaluation': 5,
        'note': 'Le goûter préféré des enfants',
        'ingredients': [
            {'nom': 'Farine', 'quantite': 250, 'unite': 'g'},
            {'nom': 'Œuf', 'quantite': 4, 'unite': 'pièce'},
            {'nom': 'Lait', 'quantite': 500, 'unite': 'ml'},
            {'nom': 'Sucre', 'quantite': 50, 'unite': 'g'},
            {'nom': 'Beurre', 'quantite': 50, 'unite': 'g'},
            {'nom': 'Sel', 'quantite': 2, 'unite': 'g'},
        ],
        'instructions': [
            'Mélanger la farine, le sucre et le sel',
            'Faire un puits et ajouter les œufs',
            'Incorporer progressivement le lait en fouettant',
            'Ajouter le beurre fondu',
            'Laisser reposer la pâte 1 heure',
            'Faire cuire les crêpes dans une poêle chaude',
            'Servir avec du sucre, de la confiture ou du Nutella'
        ]
    },
    {
        'nom': 'Soupe de tomates',
        'portions': 4,
        'temps_preparation': '10 min',
        'temps_cuisson': '30 min',
        'auteur_nom': 'Cuisine de saison',
        'evaluation': 4,
        'note': 'Réconfortante en hiver',
        'ingredients': [
            {'nom': 'Tomate', 'quantite': 1000, 'unite': 'g'},
            {'nom': 'Oignon', 'quantite': 1, 'unite': 'pièce'},
            {'nom': 'Ail', 'quantite': 2, 'unite': 'gousse'},
            {'nom': 'Carotte', 'quantite': 100, 'unite': 'g'},
            {'nom': "Huile d'olive", 'quantite': 30, 'unite': 'ml'},
            {'nom': 'Bouillon de légumes', 'quantite': 500, 'unite': 'ml'},
            {'nom': 'Basilic', 'quantite': 10, 'unite': 'g'},
            {'nom': 'Sel', 'quantite': 5, 'unite': 'g'},
            {'nom': 'Poivre', 'quantite': 3, 'unite': 'g'},
        ],
        'instructions': [
            'Émincer l\'oignon et l\'ail',
            'Faire revenir dans l\'huile d\'olive',
            'Ajouter les tomates coupées en morceaux',
            'Ajouter la carotte râpée',
            'Verser le bouillon et laisser mijoter 25 minutes',
            'Mixer le tout',
            'Ajouter le basilic ciselé, saler et poivrer'
        ]
    },
    {
        'nom': 'Ratatouille',
        'portions': 6,
        'temps_preparation': '20 min',
        'temps_cuisson': '40 min',
        'auteur_nom': 'Cuisine provençale',
        'evaluation': 5,
        'note': 'Meilleure le lendemain!',
        'ingredients': [
            {'nom': 'Courgette', 'quantite': 400, 'unite': 'g'},
            {'nom': 'Aubergine', 'quantite': 400, 'unite': 'g'},
            {'nom': 'Poivron', 'quantite': 300, 'unite': 'g'},
            {'nom': 'Tomate', 'quantite': 500, 'unite': 'g'},
            {'nom': 'Oignon', 'quantite': 2, 'unite': 'pièce'},
            {'nom': 'Ail', 'quantite': 3, 'unite': 'gousse'},
            {'nom': "Huile d'olive", 'quantite': 60, 'unite': 'ml'},
            {'nom': 'Thym', 'quantite': 5, 'unite': 'g'},
            {'nom': 'Sel', 'quantite': 8, 'unite': 'g'},
            {'nom': 'Poivre', 'quantite': 3, 'unite': 'g'},
        ],
        'instructions': [
            'Couper tous les légumes en dés',
            'Faire revenir l\'oignon et l\'ail dans l\'huile',
            'Ajouter les aubergines et faire revenir 5 minutes',
            'Ajouter les courgettes et les poivrons',
            'Ajouter les tomates, le thym, sel et poivre',
            'Laisser mijoter 40 minutes à feu doux',
            'Servir chaud ou froid'
        ]
    }
]


def populate_recettes():
    """Ajouter des recettes de base"""
    app = create_app()

    with app.app_context():
        print("👨‍🍳 Ajout de recettes de base...")

        # Récupérer le premier utilisateur
        user = User.query.first()
        if not user:
            print("❌ Aucun utilisateur trouvé. Veuillez créer un utilisateur d'abord.")
            return

        print(f"✅ Utilisateur trouvé: {user.username}")

        count_added = 0
        count_skipped = 0

        for recette_data in RECETTES_BASE:
            # Vérifier si la recette existe déjà
            existing = Recette.query.filter_by(nom=recette_data['nom']).first()
            if existing:
                print(f"  ⏭️  Recette '{recette_data['nom']}' existe déjà")
                count_skipped += 1
                continue

            # Créer la recette
            recette = Recette(
                nom=recette_data['nom'],
                portions=recette_data['portions'],
                temps_preparation=recette_data.get('temps_preparation'),
                temps_cuisson=recette_data.get('temps_cuisson'),
                auteur_nom=recette_data.get('auteur_nom'),
                evaluation=recette_data.get('evaluation', 0),
                note=recette_data.get('note'),
                created_by=user.id
            )
            db.session.add(recette)
            db.session.flush()

            # Ajouter les ingrédients
            ingredients_manquants = []
            for ing_data in recette_data['ingredients']:
                ingredient = Ingredient.query.filter_by(nom=ing_data['nom']).first()
                if not ingredient:
                    ingredients_manquants.append(ing_data['nom'])
                    continue

                recette_ingredient = RecetteIngredient(
                    recette_id=recette.id,
                    ingredient_id=ingredient.id,
                    quantite=ing_data['quantite'],
                    unite=ing_data['unite']
                )
                db.session.add(recette_ingredient)

            # Ajouter les instructions
            for ordre, texte in enumerate(recette_data['instructions'], start=1):
                instruction = Instruction(
                    recette_id=recette.id,
                    ordre=ordre,
                    texte=texte
                )
                db.session.add(instruction)

            if ingredients_manquants:
                print(f"  ⚠️  '{recette_data['nom']}' - Ingrédients manquants: {', '.join(ingredients_manquants)}")
            else:
                print(f"  ✅ Ajoutée: {recette_data['nom']} ({len(recette_data['ingredients'])} ingrédients, {len(recette_data['instructions'])} étapes)")

            count_added += 1

        db.session.commit()

        print(f"\n📊 Résumé:")
        print(f"  ✅ {count_added} recettes ajoutées")
        print(f"  ⏭️  {count_skipped} recettes déjà présentes")
        print("\n✨ Terminé! Vos recettes sont prêtes à être utilisées.")


if __name__ == '__main__':
    populate_recettes()
