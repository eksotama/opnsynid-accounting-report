# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'KOI Accounting - Report General Ledger',
    'version': '8.0.1.0.0',
    'author': 'Kawula OpenERP Indonesia; Andhitia Rama & Michael Viriyananda',
    'category': 'Accounting',
    'summary': 'Report General Ledger',
    'description': """

    """,
    'website': 'https://opensynergy-indonesia.com',
    'images': [],
    'depends': [
        'account_accountant',
        'report_aeroo'
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/report_general_ledger.xml',
        'wizard/wizard_general_ledger.xml',
        'menu_Accounting.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'AGPL-3'
}