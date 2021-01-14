# -*- coding: utf-8 -*-
from openerp import http

# class BaronSalesRepresentative(http.Controller):
#     @http.route('/baron_sales_representative/baron_sales_representative/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/baron_sales_representative/baron_sales_representative/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('baron_sales_representative.listing', {
#             'root': '/baron_sales_representative/baron_sales_representative',
#             'objects': http.request.env['baron_sales_representative.baron_sales_representative'].search([]),
#         })

#     @http.route('/baron_sales_representative/baron_sales_representative/objects/<model("baron_sales_representative.baron_sales_representative"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('baron_sales_representative.object', {
#             'object': obj
#         })