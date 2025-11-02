"""
Script pour mettre à jour les lieux de rangement des ingrédients existants
"""
from app import create_app, db
from app.models import Ingredient

# Mapping des ingrédients vers leurs lieux de rangement
STORAGE_MAPPING = {
    # Fruits & Légumes
    'Pomme de terre': 'Placard sec',
    'Carotte': 'Frigo (bac à légumes)',
    'Oignon': 'Placard sec',
    'Tomate': 'Corbeille à fruits',
    'Courgette': 'Frigo (bac à légumes)',
    'Poivron': 'Frigo (bac à légumes)',
    'Salade verte': 'Frigo (bac à légumes)',
    'Ail': 'Placard sec',
    'Échalote': 'Placard sec',
    'Poireau': 'Frigo (bac à légumes)',
    'Champignon de Paris': 'Frigo (bas)',
    'Brocoli': 'Frigo (bac à légumes)',
    'Chou-fleur': 'Frigo (bac à légumes)',
    'Épinard': 'Frigo (bac à légumes)',
    'Haricot vert': 'Frigo (bac à légumes)',
    'Banane': 'Corbeille à fruits',
    'Pomme': 'Corbeille à fruits',
    'Orange': 'Corbeille à fruits',
    'Citron': 'Frigo (porte)',

    # Viandes & Poissons
    'Poulet': 'Frigo (bas)',
    'Bœuf (steak)': 'Frigo (bas)',
    'Porc': 'Frigo (bas)',
    'Saumon': 'Frigo (bas)',
    'Cabillaud': 'Frigo (bas)',
    'Jambon blanc': 'Frigo (milieu)',
    'Lardons': 'Frigo (milieu)',
    'Saucisse': 'Frigo (bas)',

    # Produits laitiers
    'Lait': 'Frigo (porte)',
    'Beurre': 'Frigo (porte)',
    'Crème fraîche': 'Frigo (haut)',
    'Yaourt nature': 'Frigo (haut)',
    'Fromage râpé': 'Frigo (milieu)',
    'Mozzarella': 'Frigo (milieu)',
    'Parmesan': 'Frigo (milieu)',
    'Fromage de chèvre': 'Frigo (milieu)',
    'Œuf': 'Frigo (porte)',

    # Épicerie salée
    'Sel': 'Placard sec',
    'Poivre': 'Placard épices',
    'Farine': 'Placard sec',
    'Bouillon cube': 'Placard sec',
    'Levure chimique': 'Placard sec',

    # Épicerie sucrée
    'Sucre': 'Placard sec',
    'Chocolat noir': 'Placard sec',
    'Miel': 'Placard sec',
    'Confiture': 'Frigo (porte)',

    # Pâtes & Riz
    'Pâtes': 'Placard sec',
    'Riz blanc': 'Placard sec',
    'Riz basmati': 'Placard sec',
    'Quinoa': 'Placard sec',
    'Semoule': 'Placard sec',

    # Conserves
    'Tomate pelée (conserve)': 'Placard sec',
    'Coulis de tomate': 'Placard sec',
    'Thon (conserve)': 'Placard sec',
    'Maïs (conserve)': 'Placard sec',
    'Haricot rouge (conserve)': 'Placard sec',
    'Pois chiche (conserve)': 'Placard sec',

    # Condiments & Sauces
    "Huile d'olive": 'Placard sec',
    'Huile de tournesol': 'Placard sec',
    'Vinaigre balsamique': 'Placard sec',
    'Vinaigre de vin': 'Placard sec',
    'Moutarde': 'Frigo (porte)',
    'Ketchup': 'Frigo (porte)',
    'Mayonnaise': 'Frigo (porte)',
    'Sauce soja': 'Placard sec',

    # Herbes & Épices
    'Basilic': 'Frigo (bac à légumes)',
    'Persil': 'Frigo (bac à légumes)',
    'Thym': 'Placard épices',
    'Laurier': 'Placard épices',
    'Origan': 'Placard épices',
    'Paprika': 'Placard épices',
    'Cumin': 'Placard épices',
    'Curry': 'Placard épices',
    'Gingembre': 'Frigo (bac à légumes)',

    # Pain & Viennoiseries
    'Pain': 'Placard sec',
    'Pain de mie': 'Placard sec',

    # Surgelés
    'Petits pois surgelés': 'Congélateur',
    'Haricot vert surgelé': 'Congélateur',
    'Épinard surgelé': 'Congélateur',

    # Boissons
    'Eau': 'Placard sec',
    "Jus d'orange": 'Frigo (porte)',
}


def update_storage_locations():
    """Mettre à jour les lieux de rangement des ingrédients existants"""
    app = create_app()

    with app.app_context():
        print("🔄 Mise à jour des lieux de rangement des ingrédients...")

        count_updated = 0
        count_not_found = 0
        count_already_set = 0

        for nom, lieu_rangement in STORAGE_MAPPING.items():
            ingredient = Ingredient.query.filter_by(nom=nom).first()

            if ingredient:
                if ingredient.lieu_rangement:
                    print(f"  ⏭️  '{nom}' a déjà un lieu de rangement: {ingredient.lieu_rangement}")
                    count_already_set += 1
                else:
                    ingredient.lieu_rangement = lieu_rangement
                    print(f"  ✅ Mis à jour: {nom} → {lieu_rangement}")
                    count_updated += 1
            else:
                print(f"  ❌ Ingrédient non trouvé: {nom}")
                count_not_found += 1

        db.session.commit()

        print(f"\n📊 Résumé:")
        print(f"  ✅ {count_updated} ingrédients mis à jour")
        print(f"  ⏭️  {count_already_set} ingrédients avaient déjà un lieu")
        print(f"  ❌ {count_not_found} ingrédients non trouvés")
        print("\n✨ Terminé!")


if __name__ == '__main__':
    update_storage_locations()
