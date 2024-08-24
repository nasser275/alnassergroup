odoo.define('pos_delivery_service.load_data_delivery', function (require) {
    "use strict";


    var models = require('point_of_sale.models');

    models.PosModel = models.PosModel.extend({
        get_product_qty_by_id: function (id) {

            var products_quantity = this.env.pos.products_quantity;
            var product_quantity_keys = Object.keys(products_quantity);

            var position = product_quantity_keys.indexOf((id).toString());
            var num_id = (id).toString()

            console.log("ID",num_id);
            console.log("position",position);
            if (position >= 0) {

                    if (products_quantity[(id).toString()].quantity > 0){
                    return products_quantity[(id).toString()].quantity;
                    }
                    else{
                    return false;
                    }
                }
            else{
                return false;
            }

        }
});


    models.load_models({
        model: 'hr.employee',
        domain: [['is_delivery_person', '=', true]],
        loaded: function (self, delivery_persons) {
            self.delivery_persons = delivery_persons;
        }
    });
    models.load_models({
        model: 'product.product',
        domain: [['is_gift', '=', true], ['available_in_pos', '=', true]],
        loaded: function (self, gift_products) {
            self.gift_products = gift_products;
        }
    });
    models.load_models({
        model: 'pos.return.reasons',
        domain: [],
        loaded: function (self, return_reasons) {
            self.return_reasons = return_reasons;
        }
    });


    models.load_models({
        model: 'stock.quant',
        fields: ['location_id', 'product_id', 'quantity'],
        domain: function (self) {
            return [['location_id', '=', self.config.stock_location_id[0]]];
        },
        loaded: function (self, products_quantity) {
            var product_available_id = {};
            var a = 0
            _.each(products_quantity, function (product_quantity) {
                 a ++;
                console.log("product_quantity",product_quantity);
                product_available_id[product_quantity.product_id[0]] = product_quantity;
            });
            console.log("Num",a);
            self.products_quantity = product_available_id;

        },
    });


    var _super = models.Order;
    models.Order = models.Order.extend({
        export_as_JSON: function () {
            var json = _super.prototype.export_as_JSON.apply(this, arguments);
            json.delivery_person_id = this.delivery_person_id;
            json.delivery_amount = this.delivery_amount;
            json.free_delivery = this.free_delivery;
            json.is_delivery = this.is_delivery;
            json.return_reason = this.return_reason;
            return json;
        },
        init_from_JSON: function (json) {
            _super.prototype.init_from_JSON.apply(this, arguments);
            this.delivery_person_id = json.delivery_person_id;
            this.delivery_amount = json.delivery_amount;
            this.free_delivery = json.free_delivery;
            this.is_delivery = json.is_delivery;
            this.return_reason = json.return_reason;
        },


    });

    var SuperOrderLine = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function (attr, options) {
            this.is_gift = this.is_gift || false;
            SuperOrderLine.initialize.call(this, attr, options);
        },

        clone: function () {
            var orderLine = SuperOrderLine.clone.call(this);
            orderLine.is_gift = this.is_gift;
            return orderLine;
        },
        export_for_printing: function () {
            var line = SuperOrderLine.export_for_printing.apply(this, arguments);
            line.is_gift = this.is_gift;
            return line;
        },
        export_as_JSON: function () {
            var json = SuperOrderLine.export_as_JSON.call(this);
            json.is_gift = this.is_gift;
            return json;
        },
        init_from_JSON: function (json) {
            this.is_gift = json.is_gift;
            SuperOrderLine.init_from_JSON.apply(this, arguments);
        }
    });



});