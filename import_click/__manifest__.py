# Copyright 2022 IC - Serincloud
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Import click",
    "summary": "Import data created in click app",
    "version": "15.0.1.0.0",
    "category": "Account",
    "author": "Antonio Cánovas ",
    "website": "https://github.com/antoniocanovas/addons-ra/import_click",
    "license": "AGPL-3",
    "depends": ["account",
                "product_analytic"],
    "data": ["views/import_click_view.xml",
             "views/menu_views.xml",
             "views/account_move_view.xml",
             "security/ir.model.access.csv",
             "data/server_action.xml"],
    "installable": True,
}
