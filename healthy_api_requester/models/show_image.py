# -*- coding: utf-8 -*-
# from odoo import http
import base64

import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
import odoo
import odoo.modules.registry
# from odoo.tools import crop_image, topological_sort, html_escape, pycompat
from odoo import http
from odoo.http import content_disposition, dispatch_rpc, request
from odoo.addons.web.controllers.main import Binary
from odoo import SUPERUSER_ID


# def binary_content(xmlid=None, model='ir.attachment', id=None, field='datas', unique=False,
#                    filename=None, filename_field='datas_fname', download=False, mimetype=None,
#                    default_mimetype='application/octet-stream', related_id=None, access_mode=None, access_token=None,
#                    env=None):
#     print(":D", env)
#     return request.registry['ir.http'].binary_content(
#         xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
#         filename_field=filename_field, download=download, mimetype=mimetype,
#         default_mimetype=default_mimetype, related_id=related_id, access_mode=access_mode, access_token=access_token,
#         env=env)


class Binary(Binary):

    @http.route('/productimage', type='http', auth='public')
    def index(self, **args):
        product_id = args.get('product_id', False)
        if product_id:
            my_user = http.request.env['product.product'].sudo().search([('id', '=', int(product_id))])

            headers = [('Content-Type', 'image/png')]
            image_base64 = base64.b64decode(my_user.image_1920)
            headers.append(('Content-Length', len(image_base64)))
            response = request.make_response(image_base64, headers)
            return response

    # @http.route(['/web/image'], type='http',
    #             auth="public")
    # def content_image(self, xmlid=None, model='ir.attachment', id=None, field='datas',
    #                   filename_field='datas_fname', unique=None, filename=None, mimetype=None,
    #                   download=None, width=0, height=0, crop=False, related_id=None, access_mode=None,
    #                   access_token=None, avoid_if_small=False, upper_limit=False, signature=False, **kw):
    #     env = request.env
    #     status, headers, content = binary_content(
    #         xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
    #         filename_field=filename_field, download=download, mimetype=mimetype,
    #         default_mimetype='image/png', related_id=related_id, access_mode=access_mode, access_token=access_token
    #         , env=env(user=SUPERUSER_ID)
    #     )
    #     if status == 304:
    #         return werkzeug.wrappers.Response(status=304, headers=headers)
    #     elif status == 301:
    #         return werkzeug.utils.redirect(content, code=301)
    #     elif status != 200 and download:
    #         return request.not_found()
    #
    #     if headers and dict(headers).get('Content-Type', '') == 'image/svg+xml':  # we shan't resize svg images
    #         height = 0
    #         width = 0
    #     else:
    #         height = int(height or 0)
    #         width = int(width or 0)
    #
    #     if not content:
    #         content = base64.b64encode(self.placeholder(image='placeholder.png'))
    #         headers = self.force_contenttype(headers, contenttype='image/png')
    #         if not (width or height):
    #             suffix = field.split('_')[-1]
    #             if suffix in ('small', 'medium', 'big'):
    #                 content = getattr(odoo.tools, 'image_resize_image_%s' % suffix)(content)
    #
    #     # if crop and (width or height):
    #     #     try:
    #     #         content = crop_image(content, type='center', size=(width, height), ratio=(1, 1))
    #     #     except Exception:
    #     #         return request.not_found()
    #     # elif (width or height):
    #     #     if not upper_limit:
    #     #         # resize maximum 500*500
    #     #         if width > 500:
    #     #             width = 500
    #     #         if height > 500:
    #     #             height = 500
    #     #     try:
    #     #         content = odoo.tools.image_resize_image(base64_source=content, size=(width or None, height or None),
    #     #                                                 encoding='base64', upper_limit=upper_limit,
    #     #                                                 avoid_if_small=avoid_if_small)
    #     #     except Exception:
    #     #         return request.not_found()
    #
    #     image_base64 = base64.b64decode(content)
    #     headers.append(('Content-Length', len(image_base64)))
    #     response = request.make_response(image_base64, headers)
    #     response.status_code = status
    #     print("response", response)
    #     return response
