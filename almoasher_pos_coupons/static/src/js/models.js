odoo.define('almoasher_pos_coupons.models', function (require) {
    "use strict";


    var models = require('point_of_sale.models');



    var _super = models.Order;
    models.Order = models.Order.extend({
     export_for_printing: function () {
            var line = _super.prototype.export_for_printing.apply(this, arguments);
              this.pos.update_pos_coupon_data_to_backend({'coupon_id': this.coupon_id})
            return line;
        },
        export_as_JSON: function () {
            var json = _super.prototype.export_as_JSON.apply(this, arguments);
            json.coupon_id = this.coupon_id;
            return json;
        },
        init_from_JSON: function (json) {
            _super.prototype.init_from_JSON.apply(this, arguments);
            this.coupon_id = json.coupon_id;

        },
         set_client: function(client){
              var lines = this.get_orderlines();
              console.log("D<D<FMFMGGM",lines,this.get_coupon_product())
                for (const line of lines) {
                   if (this.get_coupon_product()==line.product.id){
                   line.set_quantity("remove");
                   }

                }
        this.assert_editable();
        this.set('client',client);



    },
     get_coupon_product:function() {
     var products=this.pos.db.product_by_id;
            for (var i in products) {
                if (products[i]['display_name'] == 'POS-Coupon-Product')
                    return products[i]['id'];
            }
            return false;
        }
    });



});