# -*- coding: utf-8 -*-

from openerp import models, fields, api
#import datetime
import logging
from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__) 

class ResPartner(models.Model):
    _inherit = 'res.partner'
    # keeps torgovik user that manages current company
    torgovik = fields.Many2one("res.users", string=u"Торг. представитель", domain=[('groups_id.name','=','Sales Representative')])

    # this flag is being set on a company
    is_called = fields.Boolean(string=u'Вызов на точку')

    # sale_order_ids already given in res_partner (see using ui)
    
    @api.one
    def _is_two_periods_overdued(self):
        res = self.env['baron.partners.report'].search([('partner_id', '=', self.id), ('is_overdued', '=', '2')])
        self.is_two_periods_overdued = len(res) > 0
        

    @api.model
    def create(self, vals):
        # need to set mail_create_nolog to avoid sending emails while new torgovik creates a contact within a company (email not set for partner -> error)  
        is_torgovik = self.env.user.has_group('baron_sales_representative.group_sales_representative')
        partner = super(ResPartner, self.with_context(mail_create_nolog=True) if is_torgovik else self).create(vals)
        return partner        
     
    
    #returns list of ids: gets partner with overdued invoices only if param 'is_debet_only_search' is sent 
    def _search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None):
        _search_res = super(ResPartner, self)._search(cr, user, args, offset=offset, limit=limit, order=order, context=context,
                                                count=count, access_rights_uid=access_rights_uid)
        if context:
            if 'is_debet_only_search' in context.keys():
                is_debet_only_search = context['is_debet_only_search']
                if is_debet_only_search:
                    # skip debet search for contacts of partner card (while in torgovik role). Otherwise contacts not shown.
                    if len([item for item in args if item[0] == 'parent_id']) > 0:
                        return _search_res                            
                    res = []
                    for partner_id in _search_res:
                        overdued = self.pool.get('baron.partners.report').search(cr, user, 
                            [('partner_id', '=', partner_id), ('is_overdued', 'in', ['1', '2'])], context=context)
                        if len(overdued) > 0:
                            res.append(partner_id)
                    return res
                
        return _search_res
    
    is_two_periods_overdued = fields.Boolean(string=u'Просрочка 2х и более п.', compute=_is_two_periods_overdued)      
    
# res_user class is extended to allow torgovik create child torgovik user (not partner)  
# res_user is an extension of res_partner  
class ResUsers(models.Model):
    _inherit = 'res.users'  
    
    # parent_torgovik used to create a pyramid of torgovikov
    parent_torgovik = fields.Many2one("res.users", string=u"Родительский представитель", domain=[('groups_id.name','=','Sales Representative')])      
    
    # region id
    region_id = fields.Many2one("baron.region", string=u"Регион")    
    
    @api.model
    def create(self, vals):
        context = dict(self._context or {})
        is_my_subs = False

        if 'is_my_subs' in context.keys():
            is_my_subs = context['is_my_subs']    

        # need to set mail_create_nolog to avoid sending emails while new torgovik is created by torgovik (email not set for partner -> error)     
        res = super(ResUsers, self.with_context(mail_create_nolog=True) if is_my_subs else self).create(vals)

        if is_my_subs:
            res.write({'parent_torgovik': self.env.user.id})
            res.write({'region_id': self.env.user.region_id.id}) 
            # add to torgovik group
            group_obj = self.env['ir.model.data'].get_object('baron_sales_representative', 'group_sales_representative')
            group_obj.sudo().write({'users': [(4, res.id)]})
            # remove employee group that automatically gets added to torgoviks created by torgovik
            group_obj = self.env['ir.model.data'].get_object('base', 'group_user')
            group_obj.sudo().write({'users': [(3, res.id)]})                    
        return res    
    
    
class sale_order(models.Model):
    _inherit = 'sale.order'    
    torgovik = fields.Many2one(related='partner_id.torgovik', store=True)   
    
#     @api.one
#     @api.depends('invoice_ids.state', 'invoice_ids.amount_total')
#     def _compute_dolg(self):
#         self.dolg = 0
#         if not self.invoice_ids:
#             return        
#         for invoice in self.invoice_ids:
#             if invoice.state != "paid":
#                 self.dolg += invoice.amount_total
#                     
#     @api.one
#     def _is_outdated(self):
#         self.is_outdated = False        
#         if not self.invoice_ids:
#             return  
#         today = datetime.date.today()
#         for invoice in self.invoice_ids:
#             due_date = datetime.datetime.strptime(invoice.date_due, '%Y-%m-%d').date()
#             if due_date < today:
#                 self.is_outdated = True                        
#     
#     
#     dolg = fields.Float(string=u'Дебет', compute=_compute_dolg, store=True)
#     is_outdated = fields.Boolean(string=u'Просрочен', compute=_is_outdated) 
    

class region(models.Model):
    _name = 'baron.region' 
    _order = "name"
     
    name = fields.Char(string=u"Название региона", required=True)
    level_max = fields.Integer(string=u"Кол-во уровней", default=3, help=u"Кол-во уровней вложенности")
    line_ids = fields.One2many('baron.region.line', 'region_id', string=u'Уровни региона', copy=True)      
    
    @api.one
    @api.constrains('line_ids')
    def _check_lines_max(self):
        if len(self.line_ids) > self.level_max:
            raise ValidationError(u"Превышено число возможных уровней для региона: " + str(self.level_max))      
 
     
class region_line(models.Model):   
    _name = 'baron.region.line'
        
    name = fields.Char(string=u"Название уровня")
    level_num = fields.Integer(string=u"Номер уровня", default=1)
    percent = fields.Integer(
        string=u"Процент с уровня", 
        required=True, default=0)     
    region_id = fields.Many2one('baron.region', string=u'Уровень', required=True, select=True, ondelete='cascade')  
  
    @api.model
    def create(self, vals):
        maxNum = 0
        list_ = self.search([('region_id', '=', vals["region_id"])])
        for line in list_:
            if line.level_num > maxNum:
                maxNum = line.level_num
        vals['level_num'] = maxNum + 1          
        return super(region_line, self).create(vals)  
     
    
