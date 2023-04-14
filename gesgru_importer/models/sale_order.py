from odoo import fields, models, api
from odoo.exceptions import ValidationError

class SaleOrderAlbaran(models.Model):
    _inherit = 'sale.order'

    fecha_albaran = fields.Datetime('Fecha Albaran')
    expediente = fields.Char("Expediente")
    n_rela_ser = fields.Integer("N_RELA_SER")


class SaleOrderLineAlbaran(models.Model):
    _inherit = 'sale.order.line'

    cod_mapfre = fields.Integer("Codigo Mapfre")
    cod_servicio = fields.Integer("Codigo Servicio")
