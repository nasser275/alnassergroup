odoo.define('pos_customer_wasfah.models', function (require) {
	const { Context } = owl;
	var models = require('point_of_sale.models');
	models.load_fields('res.partner', ['wasfah']);
});
