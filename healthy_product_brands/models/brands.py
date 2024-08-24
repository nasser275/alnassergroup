import logging

from odoo import api, fields, models
import requests
from .settings import get_domain_for_host_by_ip_address, chec_ip_is_live, \
    get_image_url_512_for_categ, get_image_url_for_prod

logger = logging.getLogger(__name__)


class Brands(models.Model):
    _name = 'healthy.brands'

    url_crud = '{}/api/v1/ODDO_APIS/Brands'.format(get_domain_for_host_by_ip_address())
    url_delete = '{}/api/v1/ODDO_APIS/Brands/delete_brand'.format(get_domain_for_host_by_ip_address())

    name = fields.Char(string="English Name", required=True)
    name_ar = fields.Char(string="Arabic Name", required=True)
    description_en = fields.Text(string="English Description", required=False)
    description_ar = fields.Text(string="Arabic Description", required=False)
    url_en = fields.Char(string="English Url", required=False)
    url_ar = fields.Char(string="Arabic Url", required=False)
    image = fields.Binary(string="Image")
    published = fields.Boolean(string="Published")

    @api.model
    def create(self, values):
        res = super(Brands, self).create(values)
        data = self.get_data(res)
        print(data)
        print(self.url_crud)
        if data and self.url_crud:
            try:
                response = requests.post(self.url_crud, data)
                logger.info("Create Brand:%s", response.text)
                print("Response: %s , status: %s" % (response.text, response.status_code))
            except Exception as e:
                print(e)

        return res

    def write(self, vals):
        res = super(Brands, self).write(vals)
        for rec in self:
            data = rec.get_data_update()
            try:
                response = requests.post(self.url_crud, data)
                print("Response: %s , status: %s" % (response.text, response.status_code))
            except Exception as e:
                print(e)
        return res

    def unlink(self):
        data = self.mapping_brand_delete()
        if data:
            try:
                print(data)
                response = requests.delete(self.url_delete, data=data)
                print("Response: %s , status: %s" % (response.text, response.status_code))
            except Exception as e:
                print(e)
        res = super(Brands, self).unlink()
        return res

    def mapping_brand_delete(self):
        return {
            "odoo_id": self.id,
            "token": 'PPJUfNaPjArU85LWa8gXL44Y9R6veUEUTPudxYMUZEXHpVkaSpxuXEv5RnXAXYk4DkT6YFhbDh9MVhTqYGVv26r6KqDcKueWJ3ftG2GdRQ24uGByQZDDnXwHsMsEWveh'
        }

    def get_data(self, res):
        base = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {
            'odoo_id': res.id,
            'name_en': res.name,
            'name_ar': res.name_ar,
            'description_en': res.description_en,
            'description_ar': res.description_ar,
            'published': res.published,
            'url_en': res.url_en,
            'url_ar': res.url_ar,
            # 'image': self.get_image_url_for_prod(base, res.id),
            "token": 'PPJUfNaPjArU85LWa8gXL44Y9R6veUEUTPudxYMUZEXHpVkaSpxuXEv5RnXAXYk4DkT6YFhbDh9MVhTqYGVv26r6KqDcKueWJ3ftG2GdRQ24uGByQZDDnXwHsMsEWveh'

        }

    def get_data_update(self):
        base = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {
            'odoo_id': self.id,
            'name_en': self.name,
            'name_ar': self.name_ar,
            'description_en': self.description_en,
            'description_ar': self.description_ar,
            'published': self.published,
            'url_en': self.url_en,
            'url_ar': self.url_ar,
            # 'image': self.get_image_url_for_prod(base, self.id),
            "token": 'PPJUfNaPjArU85LWa8gXL44Y9R6veUEUTPudxYMUZEXHpVkaSpxuXEv5RnXAXYk4DkT6YFhbDh9MVhTqYGVv26r6KqDcKueWJ3ftG2GdRQ24uGByQZDDnXwHsMsEWveh'

        }
