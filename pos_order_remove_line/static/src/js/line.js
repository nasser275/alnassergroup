/*
 *  Copyright 2019 LevelPrime
 *  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
 */

odoo.define("pos_order_remove_line.Orderline2", function (require) {
    "use strict";

    const Orderline = require("point_of_sale.Orderline");
    var pos_model = require('point_of_sale.models');
    var _super_orderline = pos_model.Orderline;
    pos_model.Orderline = pos_model.Orderline.extend({

            set_quantity: function (quantity, keep_price) {
                    var order = this.order;
                  var lines = order.get_orderlines();
                for (const line of lines) {
                   if (this.pos.config.healthy_fdiscount_product_id[0]==line.product.id){
                     order.remove_orderline(line);
                   }

                }

                   return _super_orderline.prototype.set_quantity.apply(this,arguments);
            },
        });

});
