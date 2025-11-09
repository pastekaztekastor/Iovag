#!/usr/bin/env python3
"""
Script d'import des recettes depuis recette.txt vers la base de données
"""
from app import create_app, db
from app.models import Recette, Ingredient, RecetteIngredient, User, Instruction
import re

app = create_app()
app.app_context().push()

# Récupérer l'utilisateur admin (mathurin)
user = User.query.filter_by(email='mathurin.champemont@icloud.com').first()
if not user:
    print("❌ Utilisateur mathurin non trouvé. Créez d'abord un compte.")
    exit(1)

# Dictionnaire de mapping pour les ingrédients
INGREDIENT_MAPPING = {
    'queue de lotte': 'Lotte (queue)',
    'jambon cru': 'Jambon cru',
    'tomates grappe': 'Tomate grappe',
    'oignons': 'Oignon',
    'basilic': 'Basilic',
    'gousse d\'ail': 'Ail',
    'gousses d\'ail': 'Ail',
    'beurre': 'Beurre',
    'vin blanc sec': 'Vin blanc sec',
    'sucre en poudre': 'Sucre en poudre',
    'piment d\'espelette': 'Piment d\'Espelette',
    'huile d\'olive': 'Huile d\'olive',
    'fleur de sel': 'Fleur de sel',
    'poisson fumé': 'Poisson fumé',
    'lardons fumés': 'Lardons fumés',
    'pommes de terre': 'Pomme de terre',
    'carottes': 'Carotte',
    'navets': 'Navet',
    'choux de bruxelles': 'Chou de Bruxelles',
    'bouquet garni': 'Bouquet garni',
    'bouillon de légumes': 'Bouillon de légumes',
    'bicarbonate de sodium': 'Bicarbonate de sodium',
    'vinaigre blanc': 'Vinaigre blanc',
    'gros sel': 'Gros sel',
    'poivre': 'Poivre',
    'filet de saumon': 'Saumon',
    'poireaux': 'Poireau',
    'oignons nouveaux': 'Oignon nouveau',
    'citron': 'Citron',
    'laurier': 'Laurier',
    'crème fraîche': 'Crème fraîche',
    'fumet de poisson': 'Fumet de poisson',
    'farine': 'Farine',
    'muscade': 'Muscade',
    'quasi de veau': 'Veau (quasi)',
    'fenouil': 'Fenouil',
    'céleri': 'Céleri (branche)',
    'thym': 'Thym',
    'lait': 'Lait',
    'sel': 'Sel',
}

# Recettes à importer
recettes_data = [
    {
        'nom': 'Cocotte de lotte au jambon cru et aux tomates confites',
        'portions': 6,
        'temps_preparation': '30 min',
        'temps_cuisson': '4 h',
        'temps_repos': '12 h',
        'instructions': """- Commencez la recette la veille : Préchauffez le four à 90°C. Lavez les tomates. Coupez-les en deux et placez-les sur la plaque du four, face coupée sur le dessus. Parsemez de fleur de sel et de sucre. Arrosez d'un filet d'huile d'olive. Laissez-les cuire au four pendant 3 heures en les retournant à mi-cuisson. Laissez reposer dans le four éteint jusqu'au lendemain.

- Continuez la recette le jour même : retirez la peau de la lotte et levez les filets le long de l'arête centrale.

- Mettez les deux filets de lotte tête-bêche, de façon à avoir une épaisseur de rôti égale d'un bout à l'autre. Saupoudrez de piment entre les deux filets.

- Faites cuire les gousses d'ail avec leur peau dans de l'eau bouillante salée pendant 20 min. Égouttez-les et pelez-les. Passez au mixeur avec les 2 tomates confites et 12 feuilles de basilic. Épluchez et émincez les oignons.

- Étalez les tranches de jambon en les faisant se chevaucher et tartinez-les avec la préparation à l'ail et la tomate. Enveloppez-en le rôti de lotte. Maintenez avec du fil de cuisine.

- Faites chauffer le beurre et 1 cuillerée à soupe d'huile d'olive dans une cocotte. Mettez-y les oignons à revenir puis ajoutez le rôti de lotte. Saisissez-le en le faisant rouler. Versez le vin blanc et ajoutez les tomates confites restantes. Laissez cuire pendant 25 à 30 min. Décorez avec quelques feuilles de basilic entières et servez aussitôt""",
        'ingredients': [
            ('Lotte (queue)', 1.5, 'kg'),
            ('Jambon cru', 12, 'tranches'),
            ('Tomate grappe', 12, 'pièce'),
            ('Oignon', 2, 'pièce'),
            ('Basilic', 1, 'bouquet'),
            ('Ail', 4, 'gousses'),
            ('Beurre', 30, 'g'),
            ('Vin blanc sec', 10, 'cl'),
            ('Sucre en poudre', 1, 'CaC'),
            ('Piment d\'Espelette', 1, 'pincée'),
            ('Huile d\'olive', 3, 'CaS'),
            ('Fleur de sel', 1, 'pincée'),
        ]
    },
    {
        'nom': 'Cocotte de légumes aux poissons fumés',
        'portions': 6,
        'temps_preparation': '45 min',
        'temps_cuisson': '55 min',
        'instructions': """- Coupez à ras la tige des choux de Bruxelles et débarrassez-les des premières feuilles abîmées, lavez-les à l'eau vinaigrée, puis rincez-les à l'eau froide. Incisez-les légèrement en croix au niveau de la tige et plongez-les dans un grand faitout d'eau bouillante salée additionnée du bicarbonate. Faites-les cuire 5 min. Égouttez-les. Faites-les cuire une deuxième fois à l'eau bouillante salée pendant 10 min. Égouttez-les.

- Épluchez les carottes, les navets et les pommes de terre et lavez-les. Coupez-les en petits morceaux. Faites chauffer l'huile dans une cocotte et faites-y revenir tous les légumes, y compris les choux de Bruxelles, avec les lardons 5 min.

- Versez ensuite le bouillon de légumes et ajoutez le bouquet garni. Faites mijoter à feu doux 20 min. Poivrez.

- Émincez pendant ce temps les poissons fumés. Ajoutez-les aux légumes et poursuivez la cuisson 15 min. Servez chaud.""",
        'ingredients': [
            ('Poisson fumé', 250, 'g'),
            ('Lardons fumés', 150, 'g'),
            ('Pomme de terre', 300, 'g'),
            ('Carotte', 300, 'g'),
            ('Navet', 300, 'g'),
            ('Chou de Bruxelles', 300, 'g'),
            ('Bouquet garni', 1, 'pièce'),
            ('Bouillon de légumes', 25, 'cl'),
            ('Huile d\'olive', 4, 'CaS'),
            ('Bicarbonate de sodium', 1, 'CaC'),
            ('Vinaigre blanc', 5, 'cl'),
            ('Gros sel', 1, 'pincée'),
            ('Poivre', 1, 'pincée'),
        ]
    },
    {
        'nom': 'Blanquette de saumon',
        'portions': 4,
        'temps_preparation': '20 min',
        'temps_cuisson': '35 min',
        'instructions': """- Pelez les carottes et coupez-les en rondelles. Précuisez-les 5 min à l'eau. Épluchez les poireaux et les oignons et émincez-les. Hachez la gousse d'ail dégermée et pelée.

- Chauffez l'huile dans une sauteuse et jetez-y les poireaux, oignons et l'ail. Faites revenir 3 min et ajoutez les carottes, le fumet, le vin blanc, le jus de citron et le laurier. Laissez frémir 10 min.

- Prélevez 2 louches de bouillon et ajoutez-y la crème. Dans une casserole, préparez un roux avec le beurre et la farine. Versez le bouillon à la crème en fouettant. Ajoutez la muscade, le poivre et faites épaissir 5 min sur feu vif.

- Coupez le poisson en gros cubes. Mettez-les dans la sauteuse et poursuivez la cuisson 5 min. Incorporez la sauce à la crème et poursuivez la cuisson 5 min en remuant délicatement. Servez rapidement avec du riz.""",
        'ingredients': [
            ('Saumon', 600, 'g'),
            ('Carotte', 3, 'pièce'),
            ('Poireau', 2, 'pièce'),
            ('Oignon nouveau', 2, 'pièce'),
            ('Citron', 1, 'pièce'),
            ('Ail', 1, 'gousse'),
            ('Laurier', 1, 'feuille'),
            ('Crème fraîche', 20, 'cl'),
            ('Beurre', 10, 'g'),
            ('Fumet de poisson', 20, 'cl'),
            ('Vin blanc sec', 10, 'cl'),
            ('Huile d\'olive', 1, 'CaS'),
            ('Farine', 1, 'CaS'),
            ('Muscade', 2, 'pincées'),
            ('Poivre', 1, 'pincée'),
        ]
    },
    {
        'nom': 'Quasi de veau braisé au lait et aux petits légumes',
        'portions': 4,
        'temps_preparation': '20 min',
        'temps_cuisson': '1 h 20',
        'instructions': """Instructions à compléter...""",
        'ingredients': [
            ('Veau (quasi)', 700, 'g'),
            ('Oignon nouveau', 12, 'pièce'),
            ('Carotte', 4, 'pièce'),
            ('Poireau', 2, 'pièce'),
            ('Fenouil', 1, 'pièce'),
            ('Céleri (branche)', 2, 'pièce'),
            ('Ail', 2, 'gousses'),
            ('Thym', 6, 'branches'),
            ('Lait', 100, 'cl'),
            ('Beurre', 40, 'g'),
            ('Huile d\'olive', 2, 'CaS'),
            ('Sel', 1, 'pincée'),
            ('Poivre', 1, 'pincée'),
        ]
    }
]

# Import des recettes
for recette_data in recettes_data:
    print(f"\n📖 Import de : {recette_data['nom']}")

    # Vérifier si la recette existe déjà
    existing = Recette.query.filter_by(nom=recette_data['nom']).first()
    if existing:
        print(f"⏭️  Recette déjà existante, ignorée")
        continue

    # Créer la recette
    recette = Recette(
        nom=recette_data['nom'],
        portions=recette_data['portions'],
        temps_preparation=recette_data['temps_preparation'],
        temps_cuisson=recette_data.get('temps_cuisson'),
        created_by=user.id,
        is_public=True,
        evaluation=4
    )

    db.session.add(recette)
    db.session.flush()  # Pour obtenir l'ID

    # Créer l'instruction (texte complet)
    instruction = Instruction(
        recette_id=recette.id,
        ordre=1,
        texte=recette_data['instructions']
    )
    db.session.add(instruction)

    # Ajouter les ingrédients
    for ing_nom, quantite, unite in recette_data['ingredients']:
        # Chercher l'ingrédient dans la BDD
        ingredient = Ingredient.query.filter_by(nom=ing_nom).first()

        if not ingredient:
            print(f"  ⚠️  Ingrédient '{ing_nom}' non trouvé dans la BDD, création...")
            ingredient = Ingredient(
                nom=ing_nom,
                categorie='Autre',
                unite_mesure=unite
            )
            db.session.add(ingredient)
            db.session.flush()

        # Créer la liaison recette-ingrédient
        recette_ingredient = RecetteIngredient(
            recette_id=recette.id,
            ingredient_id=ingredient.id,
            quantite=quantite,
            unite=unite
        )
        db.session.add(recette_ingredient)
        print(f"  ✅ {quantite} {unite} de {ing_nom}")

    db.session.commit()
    print(f"✅ Recette '{recette_data['nom']}' importée avec succès !")

print("\n" + "="*50)
print("🎉 Import terminé !")
print("="*50)
