"""add_lieu_rangement_and_inventaire_tables

Revision ID: 1760a83678c9
Revises: ac76a2ad4ac7
Create Date: 2025-11-05 01:10:33.001183

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1760a83678c9'
down_revision = 'ac76a2ad4ac7'
branch_labels = None
depends_on = None


def upgrade():
    # Créer la table inventaires
    op.create_table('inventaires',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date_inventaire', sa.DateTime(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Créer la table inventaire_items
    op.create_table('inventaire_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('inventaire_id', sa.Integer(), nullable=False),
        sa.Column('ingredient_id', sa.Integer(), nullable=False),
        sa.Column('quantite_theorique', sa.Float(), nullable=False),
        sa.Column('quantite_reelle', sa.Float(), nullable=False),
        sa.Column('ecart', sa.Float(), nullable=False),
        sa.Column('unite', sa.String(20), nullable=False),
        sa.ForeignKeyConstraint(['inventaire_id'], ['inventaires.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Supprimer les tables
    op.drop_table('inventaire_items')
    op.drop_table('inventaires')
