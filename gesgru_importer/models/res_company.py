# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models, api
import logging
from dbfread import DBF
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class GesgruImporter(models.Model):
    _inherit = 'res.company'

    last_connection_date = fields.Datetime('Last connection')
    directories = fields.Char("Directories")

    def getDbf(self, path):
        return DBF(path, ignore_missing_memofile=True, load=True)

    def parseDbfAlbaranes(self, directory, company.id):
        dbf = self.getDbf('/opt/odoo/clientes/elranero/' + directory + '/albaran.dbf')
        for i in range(len(dbf.records)):

            try:
                name = str(dbf.records[i]["NUMALB"])
                sale = self.env['sale.order'].search([('name', '=', name), ('company_id', '=', company.id)], limit=1)

                if not sale.id:

                    so = self.env['sale.order'].create({
                        'partner_id': 1,
                        'name': dbf.records[i]["NUMALB"],
                        'fecha_albaran': dbf.records[i]["FECHA"],
                        'expediente': dbf.records[i]["EXPEDIENTE"],
                        'n_rela_ser': dbf.records[i]["N_RELA_SER"],
                        'company_id': company_id
                    })
                    self.env.cr.commit()

                else:
                    sale.update({
                        'partner_id': 1,
                        'name': dbf.records[i]["NUMALB"],
                        'fecha_albaran': dbf.records[i]["FECHA"],
                        'expediente': dbf.records[i]["EXPEDIENTE"],
                        'n_rela_ser': dbf.records[i]["N_RELA_SER"],
                        'company_id': company_id
                    })
                    self.env.cr.commit()

            except Exception as ex:
                template = "- An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)


    def parseDbfLineasVenta(self, directory, company_id):
        dbf = self.getDbf('/opt/odoo/clientes/elranero/' + directory + '/contser.dbf')
        self.env.cr.commit()
        for i in range(len(dbf.records)):

            try:
                sale = self.env['sale.order'].search([('n_rela_ser', '=', str(dbf.records[i]["N_RELA_SER"]))], limit=1)
                product = self.env['product.product'].search([('default_code', '=', str(dbf.records[i]["CODIGO"]))], limit=1)

                if not product.id:
                    raise ValidationError('Crea el producto: ' + str(dbf.records[i]["CODIGO"]))

                if sale.id and product.id:

                    sol = self.env['sale.order.line'].create({
                        'order_id': sale.id,
                        'product_id': product.id,
                        'product_uom_qty': dbf.records[i]["CANTIDAD"],
                        'price_unit': dbf.records[i]["PRECIO"],
                        'name': dbf.records[i]["DESCRIPCIO"],
                        'cod_mapfre': dbf.records[i]["IDCONTSER"]
                    })

                self.env.cr.commit()

            except Exception as ex:
                template = "- An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)

    def iterateCompanies(self):
        companies = self.env['res.company'].search([('directories', '!=', '')])
        for company in companies:
            try:
                if company.directories.index(',') > 0:
                    arDirs = company.directories.split(',')
                    for iDir in arDirs:
                        self.parseDbfAlbaranes(iDir, company.id)
                        self.parseDbfLineasVenta(iDir, company.id)
            except:
                self.parseDbfAlbaranes(company.directories, company.id)
                self.parseDbfLineasVenta(company.directories, company.id)


    def import_all_action_button(self):
        '''dbf = self.getDbf('/opt/odoo/albaran.dbf')
        self.parseDbfAlbaranes(dbf)
        dbf2 = self.getDbf('/opt/odoo/contser.dbf')
        self.parseDbfLineasVenta(dbf2)'''
        self.iterateCompanies()

