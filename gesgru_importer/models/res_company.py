# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models, api
import logging
from dbfread import DBF

_logger = logging.getLogger(__name__)


class GesgruImporter(models.Model):
    _inherit = 'res.company'

    last_connection_date = fields.Datetime('Last connection')
    directories = fields.Char("Directories")

    def getDbf(self, path):
        return DBF(path, ignore_missing_memofile=True, load=True)

    def parseDbfAlbaranes(self, directory, company_id):
        dbf = self.getDbf(directory + '/albaran.dbf')
        for i in range(len(dbf.records)):

            try:
                sale = self.env['sale.order'].search([('name', '=', str(dbf.records[i]["NUMALB"])), ('company_id', '=', str(company_id))], limit=1)

                if not sale:

                    po = self.env['sale.order'].create({
                        'partner_id': 1,
                        'name': dbf.records[i]["NUMALB"],
                        'fecha_albaran': dbf.records[i]["FECHA"],
                        'expediente': dbf.records[i]["EXPEDIENTE"],
                        'n_rela_ser': dbf.records[i]["N_RELA_SER"],
                        'company_id': company_id
                    })
                    self.env.cr.commit()

                else:
                    po = self.env['sale.order'].update({
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
        dbf = self.getDbf(directory + '/contser.dbf')
        self.env.cr.commit()
        for i in range(len(dbf.records)):

            try:
                sale = self.env['sale.order'].search([('n_rela_ser', '=', str(dbf.records[i]["N_RELA_SER"]))], limit=1)
                product = self.env['product.product'].search([('default_code', '=', str(dbf.records[i]["CODIGO"]))], limit=1)

                if sale and product:

                    po = self.env['sale.order.line'].create({
                        'order_id': sale.id,
                        'product_id': product.id,
                        'product_uom_qty': dbf.records[i]["CANTIDAD"],
                        'price_unit': dbf.records[i]["PRECIO"],
                        'name': dbf.records[i]["DESCRIPCIO"],
                        'company_id': company_id,
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


    def test_action_button(self):
        '''dbf = self.getDbf('/opt/odoo/albaran.dbf')
        self.parseDbfAlbaranes(dbf)
        dbf2 = self.getDbf('/opt/odoo/contser.dbf')
        self.parseDbfLineasVenta(dbf2)'''
        self.iterateCompanies()

    # def get_purchase_order_data(self):
    # Abrimos DBF e iteramos por cada fila
    # Comprobamos si el servicio ya está definido en Odoo buscando en el modelo purchase.order por el nombre de servicio
    # po = self.env['modelo'].search(["|",('partner_ref', '=', key),], limit=1)

    # Si no está creado lo creamos con fecha y ref
    # po = self.env['modelo'].create({
    # 'state': transactions_by_state['FACTURAS'][i]['status'],
    # 'type': type_doc,
    # })
