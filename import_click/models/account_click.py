# -*- coding: utf-8 -*-
##############################################################################
#    License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
#    Copyright (C) 2021 Serincloud S.L. All Rights Reserved
#    Antonio Cánovas <antonio.canovas@ingenieriacloud.com>
#    Pedro josé Baños Guirao <pedro@serincloud.com>
##############################################################################
from odoo import api, fields, models, _
from datetime import datetime


class AccountClick(models.Model):
    _name = "import.click"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Click import"

    name = fields.Char('Name', required=True)
    invoice_export = fields.Integer('Facturas recibidas')
    invoice_import = fields.Integer('Facturas creadas')
    invoice_partner = fields.Integer('Contactos')
    data = fields.Text('Contenido')
