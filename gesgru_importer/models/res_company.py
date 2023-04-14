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

    def parseDbfAlbaranes(self, directory, company_id):
        dbf = self.getDbf('/opt/odoo/clientes/elranero/' + directory + '/albaran.dbf')

        for i in range(len(dbf.records)):
            name, fecha_albarn = dbf.records[i]["NUMALB"], dbf.records[i]["FECHA"]
            expediente, n_rela_ser = dbf.records[i]["EXPEDIENTE"], dbf.records[i]["N_RELA_SER"]

            try:
                name = str(dbf.records[i]["NUMALB"])
                sale = self.env['sale.order'].search([('name', '=', name), ('company_id', '=', company_id)], limit=1)

                if not sale.id:

                    so = self.env['sale.order'].create({
                        'partner_id': 1,
                        'name': name,
                        'fecha_albaran': fecha_albarn,
                        'expediente': expediente,
                        'n_rela_ser': n_rela_ser,
                        'company_id': company_id
                    })
                    self.env.cr.commit()

                if (sale.fecha_albaran != fecha_albaran) or (sale.expediente != expediente) or (sale.n_rela_ser != n_rela_ser):
                    sale.update({
                        'fecha_albaran': fecha_albaran,
                        'expediente': expediente,
                        'n_rela_ser': n_rela_ser,
                    })
                    self.env.cr.commit()

            except Exception as ex:
                template = "- An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)


    def parseDbfLineasVenta(self, directory, company_id):
        dbf = self.getDbf('/opt/odoo/clientes/elranero/' + directory + '/contser.dbf')
        self.env.cr.commit()

        for i in range(len(dbf.records)):
            # Variables:
            codigo, cod_mapfre = str(dbf.records[i]["CODIGO"]),  dbf.records[i]["IDCONTSER"]
            id_servicio, n_rela_ser = dbf.records[i]["IDCONTSER"], str(dbf.records[i]["N_RELA_SER"])
            cantidad, precio = dbf.records[i]["CANTIDAD"], dbf.records[i]["PRECIO"]
            nombre, cod_mapfre, actualizado = dbf.records[i]["DESCRIPCIO"], dbf.records[i]["IDCONTSER"], True

            # Si el producto no existe, que primero lo cree el cliente:
            product = self.env['product.product'].search([('default_code', '=', codigo)], limit=1)
            if (not product.id) and (codigo != ""):
                raise ValidationError('Crea el producto: ' + codigo)

            # Actualización o creación de línea de venta:
            try:
                sale = self.env['sale.order'].search([('n_rela_ser', '=', n_rela_ser)], limit=1)
                sale_line = self.env['sale.order.line'].search([('cod_mapfre', '=', cod_mapfre),
                                                                ('cod_servicio','=', id_servicio),
                                                                ('order_id','=', sale.id)], limit=1)


                if sale_line.id:
                    if (sale_line.product_id.id != product.id) or (sale_line.product_uom_qty != cantidad) \
                            or (sale_line.price_unit != precio) or (sale_line.name != nombre) or (sale_line.cod_mapfre != cod_mapfre):
                        sale_line.update({
                            'order_id': sale.id,
                            'product_id': product.id,
                            'product_uom_qty': cantidad,
                            'price_unit': precio,
                            'name': nombre,
                            'cod_mapfre': cod_mapfre
                    })
                else:
                    sol = self.env['sale.order.line'].create({
                        'order_id': sale.id,
                        'product_id': product.id,
                        'product_uom_qty': cantidad,
                        'price_unit': precio,
                        'name': nombre,
                        'cod_mapfre': cod_mapfre,
                        'cod_servicio': id_servicio,
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
                if company.directories != "":
                    self.parseDbfAlbaranes(company.directories, company.id)
                    self.parseDbfLineasVenta(company.directories, company.id)


    def import_all_action_button(self):
        '''dbf = self.getDbf('/opt/odoo/albaran.dbf')
        self.parseDbfAlbaranes(dbf)
        dbf2 = self.getDbf('/opt/odoo/contser.dbf')
        self.parseDbfLineasVenta(dbf2)'''
        self.iterateCompanies()

