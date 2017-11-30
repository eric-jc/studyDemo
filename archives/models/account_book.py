# -*- coding: utf-8 -*-

from odoo import models, fields, api
from . import bill_define


class AccountBook(models.Model):
    _name = 'archives.account_book'
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在相同账本"),
    ]
    _description = u'档案：账本'

    name = fields.Char(string=u'名称', required=True)
    company_id = fields.Many2one('res.company', string=u'公司', required=True,
                                 domain=lambda self: self.env['archives.organization'].get_company_organization())

    detail = fields.One2many('archives.account_book_detail', 'account_book_id',
                             string=u'账本明细', copy=True)
