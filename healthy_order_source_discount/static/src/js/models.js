odoo.define('healthy_order_source_discount.load_data', function (require) {
    "use strict";


    var models = require('point_of_sale.models');


    models.load_models({
        model: 'pos.order.source',
        fields: ['id', 'name','required_discount_reason','remove_promotion','show'],
        loaded: function (self, sources) {
            self.sources = sources;
        }
    });
    models.load_models({
        model: 'pos.discount.reasons',
        domain: [['show','=',true]],
        loaded: function (self, reasons) {
            self.reasons = reasons;
        }
    });


    var _super = models.Order;
    models.Order = models.Order.extend({
        export_as_JSON: function () {
            var json = _super.prototype.export_as_JSON.apply(this, arguments);
            json.order_source_id = this.order_source_id;
            json.discount_type = this.discount_type;
            json.discount_by = this.discount_by;
            json.discount_code = this.discount_code;
            json.discount_reason_id = this.discount_reason_id;
            json.discount_offer_id = this.discount_offer_id;
            return json;
        },
        init_from_JSON: function (json) {
            _super.prototype.init_from_JSON.apply(this, arguments);
            this.order_source_id = json.order_source_id;
            this.discount_type = json.discount_type;
            this.discount_by = json.discount_by;
            this.discount_code = json.discount_code;
            this.discount_reason_id = json.discount_reason_id;
            this.discount_offer_id = json.discount_offer_id;
        },
    });
    // models.Orderline = models.Orderline.extend({
    //
    //     set_product_lot: function (product) {
    //         if (product) {
    //             this.has_product_lot = product.tracking !== 'none';
    //             this.pack_lot_lines = this.has_product_lot && new PacklotlineCollection(null, {'order_line': this});
    //
    //         }
    //     },
    //
    // });



});