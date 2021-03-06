# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from . import base_infor


class Goods(base_infor.BaseInfoUnique):
    _name = 'archives.goods'
    _description = u'档案：物料'

    short_name = fields.Char(string=u'简称')

    # 通用信息
    main_unit_id = fields.Many2one('archives.unit', string=u'主单位')
    second_unit_id = fields.Many2one('archives.unit', string=u'辅单位')
    statistics_unit_id = fields.Many2one('archives.unit', string=u'统计单位')

    second_rate = fields.Float(digits=(6, 2), string=u'辅单位转换率', help=u"主单位与辅单位的换算率，如“10”，一件（辅单位）=10公斤（主单位）",
                               compute='_compute_second_rate')
    second_rate_string = fields.Char(string=u'辅单位转换率')
    statistics_rate = fields.Float(digits=(6, 2), string=u'统计单位转换率', help=u"主单位与统计单位的换算率，如“10”，一件（统计单位）=10公斤（主单位）",
                                   compute='_compute_statistics_rate')
    statistics_rate_string = fields.Char(string=u'统计单位转换率')
    need_second_change = fields.Selection([
        ('1', '是'),
        ('0', '否')
    ], string=u'辅单位是否换算', default='1')  # 不要直接使用本字段判断，使用need_change方法

    # 物料分类
    goods_type_id = fields.Many2one('archives.common_archive', string=u'物料分类')
    goods_type1_id = fields.Many2one('archives.common_archive', string=u'物料分类1')
    goods_type2_id = fields.Many2one('archives.common_archive', string=u'物料分类2')
    goods_type3_id = fields.Many2one('archives.common_archive', string=u'物料分类3')
    goods_type4_id = fields.Many2one('archives.common_archive', string=u'物料分类4')
    goods_type5_id = fields.Many2one('archives.common_archive', string=u'物料分类5')
    goods_type6_id = fields.Many2one('archives.common_archive', string=u'物料分类6')

    # 系统信息
    is_sale = fields.Boolean(string=u'用于销售')
    is_purchase = fields.Boolean(string=u'用于采购')
    is_batch_available = fields.Boolean(string=u'启用批次')

    # 权限
    organization_id = fields.Many2one('archives.common_archive', string=u'存货权限', domain="[('archive_name','=',17)]")

    @api.model
    def need_change(self):
        return self.need_second_change == '1'

    @api.depends('second_rate_string')
    def _compute_second_rate(self):
        for record in self:
            record.second_rate = float(record.second_rate_string)

    @api.depends('statistics_rate_string')
    def _compute_statistics_rate(self):
        for record in self:
            record.statistics_rate = float(record.statistics_rate_string)
