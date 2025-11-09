"""
Script pour initialiser les unités de mesure dans la base de données
"""
from app import create_app, db
from app.models import Unite

app = create_app()

with app.app_context():
    # Vérifier si des unités existent déjà
    if Unite.query.count() > 0:
        print("Les unités existent déjà dans la base de données.")
        reponse = input("Voulez-vous réinitialiser ? (o/n): ")
        if reponse.lower() != 'o':
            print("Annulation.")
            exit(0)
        # Supprimer toutes les unités existantes
        Unite.query.delete()
        db.session.commit()
        print("Unités existantes supprimées.")

    # Créer les unités de MASSE
    print("\nCréation des unités de masse...")

    # Gramme (unité de base pour la masse)
    unite_g = Unite(
        nom='gramme',
        symbole='g',
        type_unite='masse',
        unite_base_id=None,
        facteur_vers_base=1.0,
        description='Unité de base pour la masse'
    )
    db.session.add(unite_g)
    db.session.flush()  # Pour obtenir l'ID

    # Kilogramme
    unite_kg = Unite(
        nom='kilogramme',
        symbole='kg',
        type_unite='masse',
        unite_base_id=unite_g.id,
        facteur_vers_base=1000.0,
        description='1 kg = 1000 g'
    )
    db.session.add(unite_kg)

    # Milligramme
    unite_mg = Unite(
        nom='milligramme',
        symbole='mg',
        type_unite='masse',
        unite_base_id=unite_g.id,
        facteur_vers_base=0.001,
        description='1 mg = 0.001 g'
    )
    db.session.add(unite_mg)

    # Créer les unités de VOLUME
    print("Création des unités de volume...")

    # Millilitre (unité de base pour le volume)
    unite_ml = Unite(
        nom='millilitre',
        symbole='ml',
        type_unite='volume',
        unite_base_id=None,
        facteur_vers_base=1.0,
        description='Unité de base pour le volume'
    )
    db.session.add(unite_ml)
    db.session.flush()

    # Litre
    unite_l = Unite(
        nom='litre',
        symbole='L',
        type_unite='volume',
        unite_base_id=unite_ml.id,
        facteur_vers_base=1000.0,
        description='1 L = 1000 ml'
    )
    db.session.add(unite_l)

    # Centilitre
    unite_cl = Unite(
        nom='centilitre',
        symbole='cl',
        type_unite='volume',
        unite_base_id=unite_ml.id,
        facteur_vers_base=10.0,
        description='1 cl = 10 ml'
    )
    db.session.add(unite_cl)

    # Décilitre
    unite_dl = Unite(
        nom='décilitre',
        symbole='dl',
        type_unite='volume',
        unite_base_id=unite_ml.id,
        facteur_vers_base=100.0,
        description='1 dl = 100 ml'
    )
    db.session.add(unite_dl)

    # Cuillère à café
    unite_cc = Unite(
        nom='cuillère à café',
        symbole='cc',
        type_unite='volume',
        unite_base_id=unite_ml.id,
        facteur_vers_base=5.0,
        description='1 cuillère à café ≈ 5 ml'
    )
    db.session.add(unite_cc)

    # Cuillère à soupe
    unite_cs = Unite(
        nom='cuillère à soupe',
        symbole='cs',
        type_unite='volume',
        unite_base_id=unite_ml.id,
        facteur_vers_base=15.0,
        description='1 cuillère à soupe ≈ 15 ml'
    )
    db.session.add(unite_cs)

    # Tasse
    unite_tasse = Unite(
        nom='tasse',
        symbole='tasse',
        type_unite='volume',
        unite_base_id=unite_ml.id,
        facteur_vers_base=250.0,
        description='1 tasse ≈ 250 ml'
    )
    db.session.add(unite_tasse)

    # Verre
    unite_verre = Unite(
        nom='verre',
        symbole='verre',
        type_unite='volume',
        unite_base_id=unite_ml.id,
        facteur_vers_base=200.0,
        description='1 verre ≈ 200 ml'
    )
    db.session.add(unite_verre)

    # Créer les unités UNITAIRES
    print("Création des unités unitaires...")

    # Pièce
    unite_piece = Unite(
        nom='pièce',
        symbole='pièce',
        type_unite='unitaire',
        unite_base_id=None,
        facteur_vers_base=1.0,
        description='Unité de comptage (conversion dépend de l\'ingrédient)'
    )
    db.session.add(unite_piece)

    # Gousse
    unite_gousse = Unite(
        nom='gousse',
        symbole='gousse',
        type_unite='unitaire',
        unite_base_id=None,
        facteur_vers_base=1.0,
        description='Pour l\'ail, vanille, etc.'
    )
    db.session.add(unite_gousse)

    # Feuille
    unite_feuille = Unite(
        nom='feuille',
        symbole='feuille',
        type_unite='unitaire',
        unite_base_id=None,
        facteur_vers_base=1.0,
        description='Pour les feuilles (laurier, basilic, etc.)'
    )
    db.session.add(unite_feuille)

    # Sachet
    unite_sachet = Unite(
        nom='sachet',
        symbole='sachet',
        type_unite='unitaire',
        unite_base_id=None,
        facteur_vers_base=1.0,
        description='Pour les sachets (levure, thé, etc.)'
    )
    db.session.add(unite_sachet)

    # Botte
    unite_botte = Unite(
        nom='botte',
        symbole='botte',
        type_unite='unitaire',
        unite_base_id=None,
        facteur_vers_base=1.0,
        description='Pour les herbes, légumes en botte'
    )
    db.session.add(unite_botte)

    # Tranche
    unite_tranche = Unite(
        nom='tranche',
        symbole='tranche',
        type_unite='unitaire',
        unite_base_id=None,
        facteur_vers_base=1.0,
        description='Pour le pain, jambon, fromage, etc.'
    )
    db.session.add(unite_tranche)

    # Pincée
    unite_pincee = Unite(
        nom='pincée',
        symbole='pincée',
        type_unite='unitaire',
        unite_base_id=None,
        facteur_vers_base=1.0,
        description='Petite quantité d\'épices ou sel'
    )
    db.session.add(unite_pincee)

    # Sauvegarder toutes les unités
    db.session.commit()

    print(f"\n✓ {Unite.query.count()} unités créées avec succès !")

    # Afficher un résumé
    print("\nRésumé des unités créées :")
    print("\nUnités de MASSE :")
    for unite in Unite.query.filter_by(type_unite='masse').all():
        print(f"  - {unite.nom} ({unite.symbole}): facteur = {unite.facteur_vers_base}")

    print("\nUnités de VOLUME :")
    for unite in Unite.query.filter_by(type_unite='volume').all():
        print(f"  - {unite.nom} ({unite.symbole}): facteur = {unite.facteur_vers_base}")

    print("\nUnités UNITAIRES :")
    for unite in Unite.query.filter_by(type_unite='unitaire').all():
        print(f"  - {unite.nom} ({unite.symbole})")
