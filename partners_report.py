# -*- coding: utf-8 -*-
from openerp import tools, api
from openerp.osv import fields, osv
import logging

_logger = logging.getLogger(__name__) 

class partners_report(osv.osv):
    _name = "baron.partners.report"
    _description = "Torgovik partners report"
    _auto = False
    _rec_name = 'date_order'

    _columns = {

#         'date_confirm': fields.date('Date Confirm', readonly=True),
#         'product_id': fields.many2one('product.product', 'Product', readonly=True),
#         'product_uom': fields.many2one('product.uom', 'Unit of Measure', readonly=True),
#         'product_uom_qty': fields.float('# of Qty', readonly=True),

        'partner_id': fields.many2one('res.partner', u'Юр лицо', readonly=True),
        #'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'user_id': fields.many2one('res.users', u'Пользователь', readonly=True),
        #'torgovik': fields.many2one('res.partner', u'Торговый представитель', readonly=True),         
        'name': fields.char(u'Номер заказа', readonly=True),          
        'sum': fields.float(u'Оборот', readonly=True),
        'debet_amount': fields.float(u'Дебет', readonly=True),        
        'reward': fields.float(u'% с прод', readonly=True),
        'date_order': fields.datetime(u'Дата', readonly=True), 
        'parent_torgovik': fields.many2one('res.users', u'Родительский торг-к', readonly=True),
        'is_overdued': fields.selection([
            ('0', u'Нет просрочки'),
            ('1', u'Просрочка 1го периода'),
            ('2', u'Просрочка 2х и более п.') ], u'Период просрочки', readonly=True)

    }
    _order = 'date_order desc'
    
    
    @api.model
    def get_sub_award(self):
        '''
            calculate and return award from sub torgoviks (from sub levels)
        '''
        user = self.env['res.users'].browse(self._uid)
        reg = user.region_id
        total = []
        if reg:
            reg_line_percents = []
            is_first = True
            # lines are always asc by level_num because of auto_increment, so we don't care of percents order 
            for record in self.env['baron.region.line'].search([('region_id', '=', reg.id)]):
                if is_first is not True:
                    reg_line_percents.append(record.percent)
                is_first = False
            parents = [self._uid]
            i = 1
            for level_percent in reg_line_percents:
                level_total = 0
                for rec in self.search([('parent_torgovik', 'in', parents)]):
                    level_total += rec.sum * level_percent / 100
                i += 1
                total.append((level_percent, i, level_total))
                
                parents = self.get_sub_torgoviks(parents)
                if len(parents) == 0:
                    break                
                
        return {"res": total}   
     
    @api.model
    def get_sub_torgoviks(self, parents):
        res = []
        for parent in parents:
            childs = self.env['res.users'].search([('parent_torgovik', '=', parent)])
            if len(childs) > 0:
                res += map(lambda x: x.id, childs)
        return res    

             

    def _select(self):
        select_str = """
SELECT s.id as id, p.id as partner_id, u.id as user_id, s.name, 
sum(s.amount_total), 
sum(CASE
    WHEN a.state not in ('paid') THEN a.amount_total
    ELSE 0
    END) AS debet_amount,
sum(s.amount_total * coalesce(rl.percent, 0) / 100) AS reward, s.date_order, 
u.parent_torgovik,
CASE 
  WHEN a.date_due < CURRENT_DATE and a.state not in ('paid') THEN
       CASE
           WHEN s.payment_term IS NOT NULL THEN
               CASE
                   WHEN ptl.days = 0 THEN '1'
                  WHEN (CURRENT_DATE - a.date_due <= ptl.days and CURRENT_DATE - a.date_due > 0) THEN '1'
               WHEN (CURRENT_DATE - a.date_due > ptl.days) THEN '2'
            END
         ELSE '1'
    END
  ELSE '0'
END 
AS is_overdued 
        """
        return select_str

    def _from(self):
        from_str = """
sale_order s
    join account_invoice a on (s.name=a.origin)
    join res_partner p on (p.id = s.partner_id)
    join res_users u on (p.torgovik = u.id)
    left join account_payment_term pt on (s.payment_term = pt.id) 
    left join account_payment_term_line ptl on (ptl.payment_id = pt.id) 
    left join baron_region r on (u.region_id = r.id)
    left join 
         (SELECT a.*
            FROM baron_region_line a
            LEFT OUTER JOIN baron_region_line b
                ON a.region_id = b.region_id AND a.level_num > b.level_num
            WHERE b.region_id IS NULL) rl 
         on (r.id = rl.region_id)   
        """
        return from_str

    def _group_by(self):
        group_by_str = """
GROUP BY 
     s.id,
     u.id,
     p.id,     
     s.date_order,
     a.date_due,
     a.state,
     u.parent_torgovik,
     s.name,
     ptl.days 
        """
        return group_by_str

    def init(self, cr):
        # self._table = sale_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))

