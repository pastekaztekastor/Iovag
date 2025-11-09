"""
Générateur de PDF pour les recettes
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime


def generer_pdf_recette(recette, portions=None):
    """
    Génère un PDF pour une recette

    Args:
        recette: Objet Recette
        portions: Nombre de portions (optionnel, utilise recette.portions_min par défaut)

    Returns:
        BytesIO contenant le PDF
    """
    buffer = BytesIO()

    # Créer le document PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    # Styles
    styles = getSampleStyleSheet()

    # Style personnalisé pour le titre
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0d6efd'),
        spaceAfter=20,
        alignment=TA_CENTER
    )

    # Style pour les sous-titres
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#198754'),
        spaceAfter=10
    )

    # Style pour le texte normal
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_JUSTIFY
    )

    # Contenu du PDF
    story = []

    # Titre de la recette
    story.append(Paragraph(recette.nom, title_style))
    story.append(Spacer(1, 0.5*cm))

    # Informations générales
    portions_affichees = portions or recette.portions_min or 1
    info_data = [
        ['<b>Portions:</b>', str(portions_affichees)],
        ['<b>Temps de préparation:</b>', f"{recette.temps_preparation} min" if recette.temps_preparation else "Non spécifié"],
        ['<b>Évaluation:</b>', f"{recette.evaluation}/5" if recette.evaluation else "Non évaluée"],
        ['<b>Type:</b>', recette.type_repas or "Non spécifié"],
    ]

    info_table = Table(info_data, colWidths=[5*cm, 10*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    story.append(info_table)
    story.append(Spacer(1, 1*cm))

    # Ingrédients
    story.append(Paragraph("Ingrédients", subtitle_style))
    story.append(Spacer(1, 0.3*cm))

    if recette.recette_ingredients:
        ingredient_data = [['<b>Ingrédient</b>', '<b>Quantité</b>', '<b>Unité</b>']]

        for ri in recette.recette_ingredients.all():
            # Ajuster les quantités selon le nombre de portions
            quantite_base = ri.quantite
            if portions and recette.portions_min:
                ratio = portions / recette.portions_min
                quantite_affichee = round(quantite_base * ratio, 2)
            else:
                quantite_affichee = quantite_base

            ingredient_data.append([
                ri.ingredient.nom,
                str(quantite_affichee),
                ri.unite or 'g'
            ])

        ingredient_table = Table(ingredient_data, colWidths=[8*cm, 3*cm, 3*cm])
        ingredient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#198754')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        story.append(ingredient_table)
    else:
        story.append(Paragraph("<i>Aucun ingrédient défini</i>", normal_style))

    story.append(Spacer(1, 1*cm))

    # Instructions
    story.append(Paragraph("Instructions", subtitle_style))
    story.append(Spacer(1, 0.3*cm))

    if recette.instructions:
        # Diviser les instructions par lignes et numéroter
        instructions_lines = recette.instructions.split('\n')
        for i, line in enumerate(instructions_lines, 1):
            if line.strip():
                story.append(Paragraph(f"<b>{i}.</b> {line.strip()}", normal_style))
                story.append(Spacer(1, 0.2*cm))
    else:
        story.append(Paragraph("<i>Aucune instruction définie</i>", normal_style))

    story.append(Spacer(1, 1*cm))

    # Notes (si présentes)
    if recette.notes:
        story.append(Paragraph("Notes", subtitle_style))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(recette.notes, normal_style))
        story.append(Spacer(1, 1*cm))

    # Pied de page
    story.append(Spacer(1, 2*cm))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph(
        f"Recette générée le {datetime.now().strftime('%d/%m/%Y à %H:%M')} - Iovag",
        footer_style
    ))

    # Générer le PDF
    doc.build(story)

    # Réinitialiser le buffer au début
    buffer.seek(0)
    return buffer


def generer_pdf_menu(menu):
    """
    Génère un PDF pour un menu de la semaine

    Args:
        menu: Objet Menu

    Returns:
        BytesIO contenant le PDF
    """
    buffer = BytesIO()

    # Créer le document PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    # Styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0d6efd'),
        spaceAfter=20,
        alignment=TA_CENTER
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#198754'),
        spaceAfter=10
    )

    # Contenu
    story = []

    # Titre
    story.append(Paragraph(f"Menu: {menu.nom}", title_style))
    story.append(Spacer(1, 0.5*cm))

    # Date de début et nombre de convives
    info = f"Début: {menu.date_debut.strftime('%d/%m/%Y')} | Convives: {menu.nb_convives}"
    story.append(Paragraph(info, styles['Normal']))
    story.append(Spacer(1, 1*cm))

    # Jours de la semaine
    jours_ordre = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

    for jour in jours_ordre:
        # Récupérer les plats pour ce jour
        menu_jours = menu.jours.filter_by(jour_semaine=jour).all()

        if menu_jours:
            story.append(Paragraph(jour, subtitle_style))

            for mj in menu_jours:
                if mj.recette:
                    plat_text = f"<b>{mj.type_repas}:</b> {mj.recette.nom}"
                    if mj.nb_fois > 1:
                        plat_text += f" (×{mj.nb_fois})"
                    story.append(Paragraph(plat_text, styles['Normal']))
                    story.append(Spacer(1, 0.2*cm))

            story.append(Spacer(1, 0.5*cm))

    # Gâteaux (si présents)
    if menu.gateaux.count() > 0:
        story.append(Paragraph("Gâteaux", subtitle_style))
        for gateau in menu.gateaux.all():
            if gateau.recette:
                gateau_text = f"• {gateau.recette.nom}"
                if gateau.nb_fois > 1:
                    gateau_text += f" (×{gateau.nb_fois})"
                story.append(Paragraph(gateau_text, styles['Normal']))
                story.append(Spacer(1, 0.2*cm))
        story.append(Spacer(1, 0.5*cm))

    # Pied de page
    story.append(Spacer(1, 2*cm))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph(
        f"Menu généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} - Iovag",
        footer_style
    ))

    # Générer le PDF
    doc.build(story)

    buffer.seek(0)
    return buffer
