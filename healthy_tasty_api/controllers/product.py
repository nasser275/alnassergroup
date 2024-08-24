# -*- coding: utf-8 -*-
from odoo import http,models,fields
from odoo.http import Controller, request, route
from .config import validate_data,get_image_url_for_prod

class APIProduct(http.Controller):

    @http.route('/api/v1/product/list', type='json', auth="none", methods=['GET'])
    def list(self, **args):
        data = http.request.jsonrequest
        token=data.get('healthy_tasty_token')
        limit = data.get('limit', None)
        offset = data.get('start', 0)
        is_feature = data.get('is_feature', False)
        is_popular = data.get('is_popular', False)
        products_ids = data.get('products_ids')
        order_by = data.get('order_by', None)
        categ_ids = data.get('categ_ids')
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response=validate_data(str(token),api_token)
        prom_products=self.get_prom_products()
        if response:
            return response
        else:
            fields=self.get_fields()
            domain=[]
            if is_feature:
                domain.append(('is_feature','=',True))
            if is_popular:
                domain.append(('is_popular','=',True))
            if products_ids:
                domain.append(('id', 'in', products_ids))
            if categ_ids:
                domain.append(('categ_id', 'in', categ_ids))

            if prom_products:
                domain.append(('id', 'not in', prom_products))
            products = request.env['product.product'].sudo().search(domain,limit=limit,offset=offset,order=order_by)
            vals = []
            for product in products:
                val={}
                for field in fields:
                    if '.display_name' in field:
                        field=field.split('.')[0]
                        val.update({
                            field.replace('.','_')+'_name': getattr(product, field).display_name
                        })
                    elif '.id' in field:
                        field = field.split('.')[0]
                        val.update({
                            field: getattr(product, field).id
                        })
                    elif 'image' in field:
                        base = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        field = field.split('.')[0]
                        val.update({
                            field: get_image_url_for_prod(base,product.id)
                        })
                    else:
                        val.update({
                            field:getattr(product,field)
                        })
                vals.append(val)
            return {'result': vals}

    @http.route('/api/v1/product', type='json', auth="none", methods=['GET'])
    def product(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        product_id = data.get('product_id')
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        if response:
            return response
        else:
            fields = self.get_fields()
            if product_id:
                products = request.env['product.product'].sudo().search([('id','=',int(product_id))])
            else:
                products=[]
            vals = []
            for product in products:
                val = {}
                for field in fields:
                    if '.display_name' in field:
                        field = field.split('.')[0]
                        val.update({
                            field.replace('.', '_') + '_name': getattr(product, field).display_name
                        })
                    elif '.id' in field:
                        field = field.split('.')[0]
                        val.update({
                            field: getattr(product, field).id
                        })
                    elif 'image' in field:
                        base = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        field = field.split('.')[0]
                        val.update({
                            field: get_image_url_for_prod(base,product.id)
                        })
                    else:
                        val.update({
                            field: getattr(product, field)
                        })
                vals.append(val)
            return {'result': vals}

    @http.route('/api/v1/categ/product/list', type='json', auth="none", methods=['GET'])
    def list_prods_categ(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        limit = data.get('limit', None)
        offset = data.get('start', 0)
        categ_id = data.get('categ_id')
        is_feature = data.get('is_feature', False)
        is_popular = data.get('is_popular', False)
        order_by = data.get('order_by', None)
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        if response:
            return response
        else:
            fields = self.get_fields()
            if categ_id:
                domain = [('categ_id','=',int(categ_id))]
                if is_feature:
                    domain.append(('is_feature', '=', True))
                if is_popular:
                    domain.append(('is_popular', '=', True))
                products = request.env['product.product'].sudo().search(domain, limit=limit, offset=offset,order=order_by)
            else:
                products=[]
            vals = []
            for product in products:
                val = {}
                for field in fields:
                    if '.display_name' in field:
                        field = field.split('.')[0]
                        val.update({
                            field.replace('.', '_') + '_name': getattr(product, field).display_name
                        })
                    elif '.id' in field:
                        field = field.split('.')[0]
                        val.update({
                            field: getattr(product, field).id
                        })
                    elif 'image' in field:
                        base = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        field = field.split('.')[0]
                        val.update({
                            field: get_image_url_for_prod(base,product.id)
                        })
                    else:
                        val.update({
                            field: getattr(product, field)
                        })
                vals.append(val)
            return {'result': vals}

    def get_fields(self):
        product_fields = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.product_fields')
        fields=['id']
        try:
            fields=eval(product_fields)
        except:
            pass
        return fields

    def _get_lines(self,no_of_products):
        from calendar import monthrange
        from datetime import datetime
        def number_of_days_in_month(year, month):
            return monthrange(year, month)[1]
        current=datetime.now().date()
        date_from=current.replace(day=1)
        date_to=current.replace(day=number_of_days_in_month(current.year,current.month))

        where = "date(pos_order.date_order)>=\'" + str(date_from) + "\'"
        where += " and date(pos_order.date_order)<=\'" + str(date_to) + "\'"
        where += " and pos_order.state not in ('draft','cancel')"
        query = """
               select pos_order_line.product_id as product_id,count(pos_order_line.product_id) as count_product
               from pos_order_line 
               join pos_order on pos_order.id=pos_order_line.order_id
               where {where}
               group by pos_order_line.product_id order by count_product desc
               limit {no_of_products}
               """.format(where=where,no_of_products=no_of_products)
        print(">>W",query)
        request._cr.execute(query)
        lines = request._cr.dictfetchall()
        products=[]
        for line in lines:
            products.append(line.get('product_id'))
        return products

    @http.route('/api/v1/product/top', type='json', auth="none", methods=['GET'])
    def top(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        no_of_products = data.get('no_of_products', 1)
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        if response:
            return response
        else:
            fields = self.get_fields()
            products = self._get_lines(no_of_products)
            print(">D", products)
            products = request.env['product.product'].sudo().browse(products)
            vals = []
            for product in products:
                val = {}
                for field in fields:
                    if '.display_name' in field:
                        field = field.split('.')[0]
                        val.update({
                            field.replace('.', '_') + '_name': getattr(product, field).display_name
                        })
                    elif '.id' in field:
                        field = field.split('.')[0]
                        val.update({
                            field: getattr(product, field).id
                        })
                    elif 'image' in field:
                        base = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        field = field.split('.')[0]
                        val.update({
                            field: get_image_url_for_prod(base, product.id)
                        })
                    else:
                        val.update({
                            field: getattr(product, field)
                        })
                vals.append(val)
            return {'result': vals}

    @http.route('/api/v1/product/search', type='json', auth="none", methods=['GET'])
    def search(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        word = data.get('word')
        limit = data.get('limit', None)
        offset = data.get('start', 0)
        order_by = data.get('order_by', None)
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        product_search_fields = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.product_search_fields') or [('name','=','word')]
        response = validate_data(str(token), api_token)
        product_search_fields=str(product_search_fields).replace('word', word)
        product_search_fields=eval(product_search_fields)
        if response:
            return response
        else:
            fields = self.get_fields()
            if product_search_fields:
                products = request.env['product.product'].sudo().search(product_search_fields,limit=limit,offset=offset,order=order_by)
            else:
                products = []
            vals = []
            for product in products:
                val = {}
                for field in fields:
                    if '.display_name' in field:
                        field = field.split('.')[0]
                        val.update({
                            field.replace('.', '_') + '_name': getattr(product, field).display_name
                        })
                    elif '.id' in field:
                        field = field.split('.')[0]
                        val.update({
                            field: getattr(product, field).id
                        })
                    elif 'image' in field:
                        base = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        field = field.split('.')[0]
                        val.update({
                            field: get_image_url_for_prod(base, product.id)
                        })
                    else:
                        val.update({
                            field: getattr(product, field)
                        })
                vals.append(val)
            return {'result': vals}


    def get_prom_products(self):
        product_ids=[]
        model_data = request.env['pos.promotion'].sudo().search([], order='id')
        for record in model_data:
            if record.promotion_type == 'quantity_discount':
                product_ids.append(record.product_id_qty.id)
            if record.promotion_type == 'discount_on_multi_product':
                for line in record.multi_products_discount_ids:
                    for product in line.product_ids:
                        product_ids.append(product.id)

            if record.promotion_type == 'discount_on_multi_category':
                if record.filter_supplier:
                    for line in record.multi_category_discount_ids:
                        for supplier in line.supplier_ids:
                            rres = request.env['product.product'].sudo().search([('supplier_id', '=', supplier.id)])
                            for product in rres:
                                product_ids.append(product.id)
                if record.filter_supplier == False:
                    for line in record.multi_category_discount_ids:
                        for categ_id in line.category_ids:
                            rres = request.env['product.product'].sudo().search([('categ_id', '=', categ_id.id)])
                            for product in rres:
                                product_ids.append(product.id)
        return product_ids



