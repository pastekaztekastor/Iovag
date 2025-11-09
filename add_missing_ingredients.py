from app import create_app, db
from app.models import Ingredient

app = create_app()
app.app_context().push()

# Liste des ingrédients à ajouter depuis recette.txt
nouveaux_ingredients = [
    # Recette 1 - Cocotte de lotte
    ("Lotte (queue)", "Poissons et fruits de mer", "kg"),
    ("Jambon cru", "Charcuterie", "tranches"),
    ("Tomate grappe", "Légumes", "pièce"),
    ("Piment d'Espelette", "Épices et condiments", "pincée"),
    ("Fleur de sel", "Épices et condiments", "pincée"),
    ("Vin blanc sec", "Liquides", "cl"),
    ("Sucre en poudre", "Base", "g"),

    # Recette 2 - Cocotte de légumes aux poissons fumés
    ("Poisson fumé", "Poissons et fruits de mer", "g"),
    ("Lardons fumés", "Charcuterie", "g"),
    ("Navet", "Légumes", "g"),
    ("Chou de Bruxelles", "Légumes", "g"),
    ("Bouquet garni", "Herbes et aromates", "pièce"),
    ("Bouillon de légumes", "Liquides", "cl"),
    ("Bicarbonate de sodium", "Base", "CaC"),
    ("Vinaigre blanc", "Épices et condiments", "cl"),
    ("Gros sel", "Épices et condiments", "g"),

    # Recette 3 - Blanquette de saumon
    ("Fumet de poisson", "Liquides", "cl"),
    ("Muscade", "Épices et condiments", "pincée"),

    # Recette 4 - Quasi de veau
    ("Veau (quasi)", "Viandes", "g"),
    ("Oignon nouveau", "Légumes", "pièce"),
    ("Fenouil", "Légumes", "pièce"),
    ("Céleri (branche)", "Légumes", "pièce"),
]

# Récupérer les ingrédients existants
existing_ingredients = {ing.nom.lower(): ing for ing in Ingredient.query.all()}

added_count = 0
skipped_count = 0

for nom, categorie, unite in nouveaux_ingredients:
    # Vérifier si l'ingrédient existe déjà (insensible à la casse)
    if nom.lower() in existing_ingredients:
        print(f"⏭️  Ignoré (existe déjà) : {nom}")
        skipped_count += 1
        continue

    # Créer le nouvel ingrédient
    ingredient = Ingredient(
        nom=nom,
        categorie=categorie,
        unite_mesure=unite
    )
    db.session.add(ingredient)
    print(f"✅ Ajouté : {nom} ({categorie}, {unite})")
    added_count += 1

# Sauvegarder
db.session.commit()

print(f"\n{'='*50}")
print(f"✨ {added_count} ingrédients ajoutés")
print(f"⏭️  {skipped_count} ingrédients déjà existants")
print(f"{'='*50}")
