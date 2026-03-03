"""criar_tabela_ncm_regra

Revision ID: 02406df23f45
Revises: 962085a78481
Create Date: 2026-03-03 13:31:46.975516

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '02406df23f45'
down_revision: Union[str, Sequence[str], None] = '962085a78481'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('ncm_regra',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('ncm_prefixo', sa.String(length=8), nullable=False),
    sa.Column('descricao', sa.String(length=200), nullable=False),
    sa.Column('estoque_minimo', sa.Integer(), nullable=False),
    sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('ncm_prefixo')
    )

    op.execute("""
        INSERT INTO ncm_regra (ncm_prefixo, descricao, estoque_minimo) VALUES
        ('3002', 'Vacinas veterinárias', 5),
        ('3004', 'Medicamentos veterinários', 5),
        ('3006', 'Seringas e agulhas', 5),
        ('3307', 'Higiene animal', 3),
        ('3808', 'Carrapaticidas, venenos e defensivos', 5),
        ('3824', 'Detergente de ordenha', 5),
        ('1004', 'Sementes de aveia', 3),
        ('1209', 'Sementes em geral', 3),
        ('2301', 'Farinha de osso e farelo proteico', 3),
        ('2309', 'Rações, sal mineral e suplementos', 5),
        ('3101', 'Fertilizantes e adubos', 3),
        ('3102', 'Fertilizantes nitrogenados', 3),
        ('3105', 'Fertilizantes compostos', 3),
        ('8201', 'Enxada, foice, facão e recolhedor', 2),
        ('8202', 'Fita de serra', 2),
        ('8205', 'Alicates, chaves e martelo', 2),
        ('8211', 'Facas e canivetes', 2),
        ('8413', 'Bombas d agua e motobombas', 1),
        ('8424', 'Pulverizadores costais', 2),
        ('8432', 'Implementos agrícolas', 1),
        ('8433', 'Roçadeiras e cortadores de grama', 1),
        ('8434', 'Produtos para ordenha', 2),
        ('8467', 'Serra elétrica', 1),
        ('3916', 'Perfis e mangueiras de gotejamento', 2),
        ('3917', 'Mangueiras e conexões', 3),
        ('8481', 'Válvulas e registros', 2),
        ('8536', 'Tomadas, interruptores e pino macho', 3),
        ('8539', 'Lâmpadas', 3),
        ('8544', 'Fios e cabos elétricos', 3),
        ('8507', 'Baterias e acumuladores', 2),
        ('7217', 'Arame em geral', 2),
        ('7308', 'Estruturas metálicas e porteiras', 1),
        ('7317', 'Grampos para cerca', 5),
        ('7318', 'Parafusos, porcas e arruelas', 5),
        ('7326', 'Tacho e arame farpado', 1),
        ('7415', 'Pregos', 5),
        ('4201', 'Arreios, coleiras e cabresto', 3),
        ('4205', 'Selas e albardas', 1),
        ('6307', 'Cordas e barbantes', 3),
        ('6210', 'Macacões, aventais e roupas', 2),
        ('6216', 'Luvas de trabalho', 3),
        ('6401', 'Botas de borracha', 2),
        ('6403', 'Botas de couro', 2),
        ('6504', 'Chapéu de palha', 3),
        ('2710', 'Óleos lubrificantes', 3),
        ('3403', 'Graxas', 2),
        ('4011', 'Pneus', 1),
        ('4016', 'Correias e peças de borracha', 2),
        ('8708', 'Peças para tratores', 1),
        ('3214', 'Massa corrida e selador', 2),
        ('3814', 'Solventes e aguarrás', 3),
        ('3910', 'Silicone', 3),
        ('9507', 'Anzóis, linhas e redes de pesca', 3),
        ('3923', 'Embalagens plásticas e baldes', 3),
        ('3925', 'Bobinas de lona', 3),
        ('3926', 'Demais plásticos', 2),
        ('7010', 'Frascos e vidros', 2),
        ('7615', 'Panelas de alumínio', 2),
        ('8716', 'Reboques e implementos', 1)
    """)


def downgrade() -> None:
    op.drop_table('ncm_regra')