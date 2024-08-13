import json
from odoo import http
from odoo.http import request

class ProductAPI(http.Controller):
 
    @http.route('/api/product/create', type='http',csrf=False, auth='user', methods=['POST'])
    def create_product(self, **kwargs):
        try:
            payload = json.loads(request.httprequest.data.decode('utf-8'))
            product_name = payload.get('product_name')
            api_id = payload.get('id', False)

            category_name = payload.get('group')
            description = payload.get('description', '')
            price = payload.get('price', 0.0)

            Product = request.env['product.template']
            Category = request.env['product.category']

            category = Category.search([('name', '=', category_name)], limit=1)
            if not category:
                category = Category.create({'name': category_name})

            product_vals = {
                'name': product_name,
                'description': description,
                'list_price': price,
                'categ_id': category.id,
                'api_id':api_id
            }
            product = Product.search([('api_id', '=', api_id)])
           
            if product:
                response = {
                    'code': 409,
                    'message': '',
                    'error': 'Product already exists.',
                    'data': {}
                } 
                response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                response_obj.status_code = 409
                return response_obj


            product = Product.create(product_vals)

            response= {
                'code': 200,
                'message': 'Product created successfully.',
                'error': '',
                'data': {
                    'product_id': product.id,
                    'action': 'created',
                    'id': product.api_id,
                    'name': product.name,
                    'description': product.description,
                    'price': product.list_price,
                    'group': category.name,
                }
            }
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 200
            return response_obj

        except Exception as e:
            response = {
                'code': 400,
                'message': '',
                'error': str(e),
                'data': {}
            }
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 400
            return response_obj

    @http.route('/api/product/update', type='http',csrf=False, auth='user', methods=['POST'])
    def update_product(self, **kwargs):
        try:
            payload = json.loads(request.httprequest.data.decode('utf-8'))
            api_id = payload.get('id')
            product_name = payload.get('product_name')
            category_name = payload.get('group')
            description = payload.get('description', '')
            price = payload.get('price', 0.0)

            Product = request.env['product.template']
            Category = request.env['product.category']

            product = Product.search([('api_id', '=', api_id)])
            if not product:
                response= {
                        'code': 404,
                        'message': 'Product not found.',
                        'error': '',
                        'data': {}
                    }
                
                response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                response_obj.status_code = 404
                return response_obj
                
            category = Category.search([('name', '=', category_name)], limit=1)
            if not category :
                category = Category.create({'name': category_name})

             
            product_vals = {}
            if product_name:
                product_vals['name'] = product_name
            if description:
                product_vals['description'] = description
            if price:
                product_vals['list_price'] = price
            if category:
                product_vals['categ_id'] = category.id
            


            product.write(product_vals)

            response= {
                'code': 200,
                'message': 'Product updated successfully.',
                'error': '',
                'data': {
                    'id': product.api_id,
                    'product_id': product.id, 
                    'action': 'updated', 
                    'name': product.name,
                    'description': product.description,
                    'price': product.list_price,
                    'group': category.name,
                }
            }
            
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 200
            return response_obj
        except Exception as e:
            response = {
                'code': 400,
                'message': '',
                'error': str(e),
                'data': {}
            }
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 400
            return response_obj

  

    @http.route('/api/product/<int:product_id>', type='http', auth='user', methods=['GET'])
    def get_product_by_id(self, product_id, **kwargs):
        try:
            Product = request.env['product.template']
            product = Product.search([('api_id', '=', product_id)], limit=1)
            if not product:
                return request.make_response(
                    json.dumps({
                        'code': 404,
                        'message': 'Product not found.',
                        'error': '',
                        'data': {}
                    }), 
                    headers={'Content-Type': 'application/json'},
                    status=404
                )

            return request.make_response(
                json.dumps({
                    'code': 200,
                    'message': '',
                    'error': '',
                    'data': {
                        'id': product.api_id,
                        'product_id': product.id,
                        'name': product.name,
                        'description': product.description,  
                        'price': product.list_price,
                        'group': product.categ_id.name,
                    }
                }),
                headers={'Content-Type': 'application/json'},
                status=200
            )

        except Exception as e:
            return request.make_response(
                json.dumps({
                    'code': 400,
                    'message': 'Internal Server Error',
                    'error': str(e),
                    'data': {}
                }),
                headers={'Content-Type': 'application/json'},
                status=400
            )


    @http.route('/api/product/list', type='http', auth='user', methods=['GET'])
    def get_product_list(self, **kwargs):
        try:
            page = int(request.params.get('page', 1))
            page_size = int(request.params.get('page_size', 10))
            search_term = request.params.get('search', '')

            Product = request.env['product.template']

            domain = [('name', 'ilike', search_term)]

            total_count = Product.search_count(domain)

            start = (page - 1) * page_size


            
            order_by = request.params.get('order_by', 'id')
            order_direction = request.params.get('order_direction', 'asc')

            if order_direction not in ['asc', 'desc']:
                order_direction = 'asc'
 
            order = f'{order_by} {order_direction}'

            products = Product.search(domain, offset=start, limit=page_size, order=order)
            

            product_list = []
            for product in products:
                product_list.append({
                    'id': product.api_id,
                    'product_id': product.id,
                    'name': product.name,
                    'description': product.description,   
                    'price': product.list_price,
                    'category': product.categ_id.name,
                })

            response_data = {
                'code': 200,
                'message': 'Product list fetched successfully.',
                'error': '',
                'data': {
                    'total_count': total_count,
                    'page': page,
                    'page_size': page_size,
                    'products': product_list,
                }
            }

            return request.make_response(
                json.dumps(response_data),
                headers={'Content-Type': 'application/json'},
                status=200
            )

        except Exception as e:
            response_data = {
                'code': 400,
                'message': 'Internal Server Error',
                'error': str(e),
                'data': {}
            }

            return request.make_response(
                json.dumps(response_data),
                headers={'Content-Type': 'application/json'},
                status=400
            )