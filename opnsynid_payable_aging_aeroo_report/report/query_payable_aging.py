# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.tools import drop_view_if_exists
from datetime import datetime


class QueryPayableAging(models.Model):

    _name = "account.query_payable_aging"
    _description = "Query Payable Aging"
    _auto = False

    @api.one
    def function_aging(self):
        res = {}
        residual = 0.0
        obj_move_line = self.env["account.move.line"]
        period_length = self._context.get("period_length", False)
        date_as_of = self._context.get("date_as_of", False)

        if date_as_of:
            ord_date_as_of = datetime.strptime(
                date_as_of, "%Y-%m-%d").toordinal()

        res = {
            "aging1": 0.0,
            "aging2": 0.0,
            "aging3": 0.0,
            "aging4": 0.0,
            "aging5": 0.0,
            "amount_residual": 0.0,
            "amount_residual_currency": 0.0,
        }

        if self.date_due:
            ord_date_due = datetime.strptime(
                self.date_due, "%Y-%m-%d").toordinal()

            direction = (ord_date_due - ord_date_as_of)
            move_line = obj_move_line.browse(self.ids)[0]

            if move_line.amount_residual:
                partial_ids = move_line.reconcile_partial_id.line_partial_ids

                if move_line.reconcile_partial_id:
                    for payment_line in partial_ids:
                        if payment_line.date <= date_as_of:
                            residual += (
                                payment_line.debit - payment_line.credit)
                else:
                    residual = move_line.amount_residual

                self.amount_residual = abs(residual)

                for interval in range(1, 6):
                    st_if_1 = period_length * (interval - 1)
                    st_if_2 = period_length * (interval)
                    if (st_if_1) <= abs(direction) < (st_if_2):
                        res["aging%s" % (interval)] = abs(residual)

                    if interval == 5:
                        if abs(direction) >= (period_length * 4):
                            res["aging5"] = abs(residual)

            if move_line.amount_residual_currency:
                residual_currency = move_line.amount_residual_currency
                self.amount_residual_currency = residual_currency

        self.aging1 = res["aging1"]
        self.aging2 = res["aging2"]
        self.aging3 = res["aging3"]
        self.aging4 = res["aging4"]
        self.aging5 = res["aging5"]

        if direction < 0:
            self.direction = "past"
        else:
            self.direction = "future"

    name = fields.Char(string="Description", size=64)

    move_id = fields.Many2one(
        string="# Move",
        comodel_name="account.move"
    )

    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account"
    )

    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company"
    )

    date = fields.Date(string="Date")
    date_due = fields.Date(string="Date Due")

    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal"
    )

    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner"
    )

    period_id = fields.Many2one(
        string="Period",
        comodel_name="account.period"
    )

    respective_currency_id = fields.Many2one(
        string="Respective Currency",
        comodel_name="res.currency"
    )

    base_currency_id = fields.Many2one(
        string="Base Currency",
        comodel_name="res.currency"
    )

    reconcile_id = fields.Many2one(
        string="Reconcile",
        comodel_name="account.move.reconcile"
    )

    reconcile_partial_id = fields.Many2one(
        string="Partial Reconcile",
        comodel_name="account.move.reconcile"
    )

    debit = fields.Float(string="Debit")
    credit = fields.Float(string="Credit")
    amount_currency = fields.Float(string="Amount Currency")

    amount_residual = fields.Float(
        string="Amount Residual",
        compute=function_aging
    )

    amount_residual_currency = fields.Float(
        string="Amount Residual Currency",
        compute=function_aging
    )

    aging1 = fields.Float(
        string="Aging1",
        compute=function_aging
    )

    aging2 = fields.Float(
        string="Aging2",
        compute=function_aging
    )

    aging3 = fields.Float(
        string="Aging3",
        compute=function_aging
    )

    aging4 = fields.Float(
        string="Aging4",
        compute=function_aging
    )

    aging5 = fields.Float(
        string="Aging5",
        compute=function_aging
    )

    direction = fields.Selection(
        string="Direction",
        selection=[("past", "Past"), ("future", "Future")],
        compute=function_aging
    )

    state = fields.Selection(
        string="State",
        selection=[("draft", "Unposted"), ("posted", "Posted")]
    )

    def init(self, cr):
        drop_view_if_exists(cr, "account_query_payable_aging")
        strSQL = """
                    CREATE OR REPLACE VIEW account_query_payable_aging AS (
                        SELECT
                                a.id AS id,
                                a.name AS name,
                                a.move_id AS move_id,
                                a.account_id AS account_id,
                                b.company_id AS company_id,
                                b.date as date,
                                a.date_maturity as date_due,
                                b.journal_id AS journal_id,
                                a.partner_id AS partner_id,
                                b.period_id AS period_id,
                                CASE
                                    WHEN a.currency_id IS NULL
                                    THEN e.currency_id
                                    ELSE a.currency_id
                                END AS respective_currency_id,
                                e.currency_id AS base_currency_id,
                                a.reconcile_id AS reconcile_id,
                                a.reconcile_partial_id AS reconcile_partial_id,
                                a.debit AS debit,
                                a.credit AS credit,
                                a.amount_currency AS amount_currency,
                                b.state AS state
                        FROM account_move_line AS a
                        JOIN account_move AS b ON a.move_id = b.id
                        JOIN account_journal AS c ON b.journal_id = c.id
                        JOIN account_account AS d ON a.account_id = d.id
                        JOIN res_company AS e ON b.company_id = e.id
                        WHERE   (d.type = 'payable') AND
                                (b.state = 'posted') AND
                                (a.credit > 0)
                    )
                    """
        cr.execute(strSQL)
