# -*- coding: utf-8 -*-

from odoo import models, fields, api
from . import bill_define


class SaleOrderDetail(models.Model):
    _name = 'jc_sale.sale_order.detail'
    _description = u'销售：销售订单明细'

    sale_order_id = fields.Many2one('jc_sale.sale_order', string='销售订单引用', required=True,
                                    ondelete='cascade', index=True, copy=False)

    source_bill_type = fields.Selection(bill_define.BILL_TYPE, string=u'来源单据类型', readonly=True, copy=False)
    source_bill_id = fields.Integer(string="来源单据号", readonly=True, copy=False, default=0)
    source_detail_id = fields.Integer(string="来源单据明细号", readonly=True, copy=False, default=0)

    goods_id = fields.Many2one('archives.goods', string=u'产品', required=True,
                               domain=lambda self: self.env['archives.organization'].get_goods_organization())
    need_second_change = fields.Selection([
        ('1', '是'),
        ('0', '否')
    ], related='goods_id.need_second_change', string=u'辅单位是否换算', default='1')
    second_unit_id = fields.Many2one('archives.unit', string=u'辅单位', compute='_set_second', store=True)
    second_unit_number = fields.Float(digits=(6, 2), string=u'辅数量')
    second_unit_number_tmp = fields.Char(string=u'辅数量')
    main_unit_id = fields.Many2one('archives.unit', string=u'主单位', compute='_set_main', store=True)
    main_unit_number = fields.Float(digits=(6, 2), string=u'主数量')
    main_unit_number_tmp = fields.Char(string=u'主数量')

    price_type_id = fields.Many2one('archives.common_archive', string=u'价类', domain="[('archive_name','=',19)]")
    class_price_id = fields.Many2one('jc_sale.class_price', string='价格单号')
    origin_price = fields.Float(digits=(6, 2), help="原价", string=u'原价')
    transfer_price = fields.Float(digits=(6, 2), help="运价", string=u'运价')

    price = fields.Float(digits=(6, 2), help="单价", string=u'单价')
    price_tmp = fields.Char(string=u'单价')
    money = fields.Float(digits=(6, 2), help="金额", string=u'金额', store=True)

    remark = fields.Char(string=u'备注')

    def _compute_money(self):
        self.money = (self.price + self.transfer_price) * self.main_unit_number

    @api.depends('goods_id')
    def _set_main(self):
        for record in self:
            record.main_unit_id = record.goods_id.main_unit_id

    @api.depends('goods_id')
    def _set_second(self):
        for record in self:
            if record.goods_id.need_change():
                record.second_unit_id = record.goods_id.second_unit_id
            else:
                record.second_unit_id = None

    @api.depends('goods_id')
    def _set_change(self):
        for record in self:
            record.need_second_change = record.goods_id.need_second_change

    @api.onchange('second_unit_number_tmp')
    def _onchange_for_second_unit_number_from_tmp(self):
        self.second_unit_number = float(self.second_unit_number_tmp)
        if not self.goods_id.need_change():
            return
        self.main_unit_number = self.goods_id.second_rate * self.second_unit_number
        self.main_unit_number_tmp = str(self.main_unit_number)
        self._compute_money()

    @api.onchange('main_unit_number_tmp')
    def _onchange_for_main_unit_number_from_tmp(self):
        self.main_unit_number = float(self.main_unit_number_tmp)
        self._compute_money()
        if not self.goods_id.need_change():
            return
        if self.goods_id.second_rate != 0:
            self.second_unit_number = self.main_unit_number / self.goods_id.second_rate
            self.second_unit_number_tmp = str(self.second_unit_number)

    @api.onchange('price_tmp')
    def _onchange_for_price_from_tmp(self):
        self.price = float(self.price_tmp)
        self._compute_money()

    @api.onchange('price', 'main_unit_number', 'transfer_price')
    def _onchange_for_money(self):
        self._compute_money()

    @api.onchange('second_unit_number')
    def _onchange_second(self):
        if not self.goods_id.need_change():
            return
        self.main_unit_number = self.goods_id.second_rate * self.second_unit_number

    @api.onchange('main_unit_number')
    def _onchange_main(self):
        if not self.goods_id.need_change():
            return
        if self.goods_id.second_rate != 0:
            self.second_unit_number = self.main_unit_number / self.goods_id.second_rate

    @api.onchange('goods_id')
    def _onchange_goods(self):
        if self.goods_id.need_change():
            self.second_unit_id = self.goods_id.second_unit_id
        else:
            self.second_unit_id = None
        self.main_unit_id = self.goods_id.main_unit_id

    @api.model
    def create(self, values):
        self._set_tmp_for_number(values)
        return super(SaleOrderDetail, self).create(values)

    def _set_tmp_for_number(self, values):
        if 'second_unit_number' in values:
            values['second_unit_number_tmp'] = str(values['second_unit_number'])
        if 'main_unit_number' in values:
            values['main_unit_number_tmp'] = str(values['main_unit_number'])
        if 'price' in values:
            values['price_tmp'] = str(values['price'])

    @api.multi
    def write(self, values):
        self._set_tmp_for_number(values)
        return super(SaleOrderDetail, self).write(values)
