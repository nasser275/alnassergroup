# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    name = fields.Char('Name', index=True, required=True, translate=True, track_visibility='onchange')

    price_changing_date = fields.Datetime(string=" Price Changing Date", required=False, track_visibility='always')
    last_change_price = fields.Float(string="Last Change Price", required=False, track_visibility='always')

    list_price = fields.Float(
        'Sales Price', default=1.0, track_visibility='onchange',
        digits='Product Price',
        help="Price at which the product is sold to customers.",
    )
    standard_price = fields.Float(
        'Cost', compute='_compute_standard_price', track_visibility='onchange',
        inverse='_set_standard_price', search='_search_standard_price',
        digits='Product Price', groups="base.group_user",
        help="""In Standard Price & AVCO: value of the product (automatically computed in AVCO).
                In FIFO: value of the last unit that left the stock (automatically computed).
                Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
                Used to compute margins on sale orders.""")

    sku_name_english = fields.Char(string="SKU Name English", )
    sku_supplier_code = fields.Char(string="SKU Supplier Code", )
    ht_sku_code = fields.Char(string="H&T SKU Code", )
    supplier_id = fields.Many2one(string="Supplier", comodel_name="res.partner", domain="[('supplier', '=', True)]", )
    original_supplier_id = fields.Many2one(string="Original Supplier", comodel_name="res.partner",
                                           domain="[('supplier', '=', True)]", )
    shelf_life = fields.Char(string="Shelf Life", )
    size = fields.Char(string="Size", )
    healty_weight = fields.Char(string="Weight GM", )
    height = fields.Char(string="Height", )
    base_width = fields.Char(string="Base Width", )
    base_depth = fields.Char(string="Base Depth", )
    storage_temprature = fields.Char(string="Storage Temprature", )
    calories = fields.Char(string="Calories", )
    sugar = fields.Char(string="Carbohydrate", )
    sodium = fields.Char(string="Sodium", )
    container_type_id = fields.Many2one(string="Container Type", comodel_name="container.type", )
    container_shape_id = fields.Many2one(string="Container Shape", comodel_name="container.shape", )
    container_material_id = fields.Many2one(string="Container Material", comodel_name="container.material", )
    content_type_id = fields.Many2one(string="Content Type", comodel_name="content.type", )
    storage_type_id = fields.Many2one(string="Storage Type", comodel_name="storage.type", )
    color_id = fields.Many2one(string="Color", comodel_name="product.color", )
    flavor_id = fields.Many2one(string="Flavor", comodel_name="product.flavor", )
    healthy = fields.Boolean(string="Healthy", )
    natural = fields.Boolean(string="Natural", )
    keto = fields.Boolean(string="Keto", )
    low_carb = fields.Boolean(string="Low Calorie", )
    low_brotein = fields.Boolean(string="Low Protein", )
    pbd = fields.Boolean(string="PBD", )
    vegan = fields.Boolean(string="Vegan", )
    vegeterian = fields.Boolean(string="Vegeterian", )
    odor_less = fields.Boolean(string="Odor Less", )
    fats_protein = fields.Char(string="Fats", )
    Protein = fields.Char(string="Protein", )
    all_data_done = fields.Boolean(string="تم ملئ جميع البيانات")
    price_changing_date = fields.Datetime(string=" Price Changing Date", required=False)
    last_change_price = fields.Float(string="Last Change Price", required=False)
    product_name_net = fields.Text(string="Product Name Net", required=False)
    product_nature = fields.Char(string="Product Nature", required=False)
    website_description = fields.Html(string="Product Info", required=False)
    display_on_mwebsite = fields.Boolean(string="Display Product On Mobile App And Website ")
    egg_allergies = fields.Boolean(string="البيض")
    gluten_allergies = fields.Boolean(string="الجلوتين")
    nuts_allergies = fields.Boolean(string="المكسرات")
    lactose_allergies = fields.Boolean(string="الالبان")
    crustacean_allergies = fields.Boolean(string="القشريات")
    peanut_allergies = fields.Boolean(string="الفول السوداني")
    meta_description = fields.Text(string='Meta')
    white_label = fields.Boolean(string='White Label')

    have_image = fields.Boolean(string='Have Image', compute='_get_image', default=False, store=True)

    @api.depends("image_1920")
    def _get_image(self):
        for rec in self:
            if rec.image_1920:
                rec.have_image = True
            else:
                rec.have_image = False

    def write(self, values):
        if 'list_price' in values.keys():
            values['price_changing_date'] = datetime.now()
            values['last_change_price'] = self.list_price
        res = super(ProductTemplate, self).write(values)
        return res

    def write(self, values):
        if 'list_price' in values.keys():
            values['price_changing_date'] = datetime.now()
            values['last_change_price'] = self.list_price
        res = super(ProductTemplate, self).write(values)
        return res

    @api.constrains("sku_supplier_code", "supplier_id", )
    def _check_sku_supplier_code(self):
        Product = self.env['product.template']
        for s in self:
            if s.sku_supplier_code and s.supplier_id:
                search_result = Product.search(
                    [('sku_supplier_code', '=', s.sku_supplier_code), ('supplier_id', '=', s.supplier_id.id),
                     ('id', '!=', s.id)])
                if search_result:
                    raise ValidationError(_("You can not insert same code with same supplier again."))

    @api.constrains("ht_sku_code")
    def _check_ht_sku_code(self):
        Product = self.env['product.template']
        for s in self:
            if s.ht_sku_code:
                search_result = Product.search([('ht_sku_code', '=', s.ht_sku_code), ('id', '!=', s.id)])
                if search_result:
                    raise ValidationError(_("H&T SKU Code must be uniqe and it's already exist."))


class ProductColors(models.Model):
    _name = 'product.color'

    name = fields.Char(string="Name", required=True, copy=False, index=True)


class StorageType(models.Model):
    _name = 'storage.type'

    name = fields.Char(string="Name", required=True, copy=False, index=True)


class ContainerType(models.Model):
    _name = 'container.type'

    name = fields.Char(string="Name", required=True, copy=False, index=True)


class ContainerShape(models.Model):
    _name = 'container.shape'

    name = fields.Char(string="Name", required=True, copy=False, index=True)


class ContainerMaterial(models.Model):
    _name = 'container.material'

    name = fields.Char(string="Name", required=True, copy=False, index=True)


class ContentType(models.Model):
    _name = 'content.type'

    name = fields.Char(string="Name", required=True, copy=False, index=True)


class ProductFlavor(models.Model):
    _name = 'product.flavor'

    name = fields.Char(string="Name", required=True, copy=False, index=True)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    last_name = fields.Char(string="Name", track_visibility='always', )

    @api.onchange('name')
    def onchange_last_name(self):
        self.last_name = self.name

    standard_price = fields.Float(
        'Cost', company_dependent=True,
        digits='Product Price',
        groups="base.group_user",
        help="""In Standard Price & AVCO: value of the product (automatically computed in AVCO).
              In FIFO: value of the last unit that left the stock (automatically computed).
              Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
              Used to compute margins on sale orders.""", track_visibility='onchange', )
    lst_price = fields.Float(
        'Sales Price', compute='_compute_product_lst_price', track_visibility='onchange',
        digits='Product Price', inverse='_set_product_lst_price',
        help="The sale price is managed from the product template. Click on the 'Configure Variants' button to set the extra attribute prices.")

    meta_description = fields.Text(string='Meta')
    white_label = fields.Boolean(string='White Label')

    have_image = fields.Boolean(string='Have Image', compute='_get_image', default=False, store=True)

    @api.depends("image_1920")
    def _get_image(self):
        for rec in self:
            if rec.image_1920:
                rec.have_image = True
            else:
                rec.have_image = False

    def get_product_info_pos(self, price, quantity, pos_config_id):
        res = super().get_product_info_pos(price, quantity, pos_config_id)
        vals = {'Protein': {'string': 'Protein', 'value': self.Protein},
                'base_depth': {'string': 'Base Depth', 'value': self.base_depth},
                'base_width': {'string': 'Base Width', 'value': self.base_width},
                'calories': {'string': 'Calories', 'value': self.calories},
                'color_id': {'string': 'Color', 'value': self.color_id.name},
                'container_material_id': {'string': 'Container Material', 'value': self.container_material_id.name},
                'container_shape_id': {'string': 'Container Shape', 'value': self.container_shape_id.name},
                'container_type_id': {'string': 'Container Type', 'value': self.container_type_id.name},
                'content_type_id': {'string': 'Content Type', 'value': self.content_type_id.name},
                'crustacean_allergies': {'string': 'القشريات', 'value': self.crustacean_allergies},
                'supplier_id': {'string': 'Supplier ', 'value': self.supplier_id.name},
                'egg_allergies': {'string': 'البيض', 'value': self.egg_allergies},
                'fats_protein': {'string': 'Fats', 'value': self.fats_protein},
                'flavor_id': {'string': 'Flavor', 'value': self.flavor_id.name},
                'gluten_allergies': {'string': 'الجلوتين', 'value': self.gluten_allergies},
                'healthy': {'string': 'Healthy', 'value': self.healthy},
                'healty_weight': {'string': 'Weight GM', 'value': self.healty_weight},
                'height': {'string': 'Height', 'value': self.height},
                'ht_sku_code': {'string': 'H&T SKU Code', 'value': self.ht_sku_code},
                'keto': {'string': 'Keto', 'value': self.keto},
                'lactose_allergies': {'string': 'الالبان', 'value': self.lactose_allergies},
                'low_brotein': {'string': 'Low Protein', 'value': self.low_brotein},
                'low_carb': {'string': 'Low Calorie', 'value': self.low_carb},
                'natural': {'string': 'Natural', 'value': self.natural},
                'nuts_allergies': {'string': 'المكسرات', 'value': self.nuts_allergies},
                'odor_less': {'string': 'Odor Less', 'value': self.odor_less},
                'original_supplier_id': {'string': 'Original Supplier', 'value': self.original_supplier_id.name},
                'pbd': {'string': 'PBD', 'value': self.pbd},
                'peanut_allergies': {'string': 'الفول السوداني', 'value': self.peanut_allergies},
                'price_changing_date': {'string': ' Price Changing Date', 'value': self.price_changing_date},
                'product_name_net': {'string': 'Product Name Net', 'value': self.product_name_net},
                'product_nature': {'string': 'Product Nature', 'value': self.product_nature},
                'shelf_life': {'string': 'Shelf Life', 'value': self.shelf_life},
                'size': {'string': 'Size', 'value': self.size},
                'sku_name_english': {'string': 'SKU Name English', 'value': self.sku_name_english},
                'sku_supplier_code': {'string': 'SKU Supplier Code', 'value': self.sku_supplier_code},
                'sodium': {'string': 'Sodium', 'value': self.sodium},
                'storage_temprature': {'string': 'Storage Temprature', 'value': self.storage_temprature},
                'storage_type_id': {'string': 'Storage Type', 'value': self.storage_type_id.name},
                'sugar': {'string': 'Carbohydrate', 'value': self.sugar},
                'vegan': {'string': 'Vegan', 'value': self.vegan},
                'white_label': {'string': 'White Label', 'value': self.white_label},
                'meta_description': {'string': 'Meta', 'value': self.meta_description},
                'have_image': {'string': 'have_image', 'value': self.have_image},
                'vegeterian': {'string': 'Vegeterian', 'value': self.vegeterian},
                }
        vals_keys = ['Protein', 'supplier_id', 'base_depth', 'base_width', 'calories', 'color_id',
                     'container_material_id', 'container_shape_id', 'container_type_id', 'content_type_id',
                     'crustacean_allergies', 'egg_allergies', 'fats_protein', 'flavor_id',
                     'gluten_allergies', 'healthy', 'healty_weight', 'height', 'ht_sku_code', 'keto',
                     'lactose_allergies', 'low_brotein', 'low_carb', 'natural', 'nuts_allergies',
                     'odor_less', 'original_supplier_id', 'pbd', 'peanut_allergies', 'price_changing_date',
                     'product_name_net', 'product_nature', 'shelf_life', 'size', 'sku_name_english',
                     'sku_supplier_code', 'sodium', 'storage_temprature', 'storage_type_id', 'sugar', 'vegan',
                     'white_label', 'meta_description', 'have_image',
                     'vegeterian']
        # Optional products
        res['product_details'] = vals
        res['product_details_keys'] = vals_keys
        return res


class PosOrderReport(models.Model):
    _inherit = "report.pos.order"

    supplier_id = fields.Many2one(string="Supplier", comodel_name="res.partner", domain="[('supplier', '=', True)]", )

    def _select(self):
        return super(PosOrderReport, self)._select() + ", pt.supplier_id"

    def _group_by(self):
        return super(PosOrderReport, self)._group_by() + ",pt.supplier_id"
