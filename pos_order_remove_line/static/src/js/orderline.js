/*
 *  Copyright 2019 LevelPrime
 *  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
 */

odoo.define("pos_order_remove_line.Orderline", function (require) {
    "use strict";

    const Orderline = require("point_of_sale.Orderline");
    const Registries = require("point_of_sale.Registries");

    const PosOrderline = (Orderline) =>
        class extends Orderline {
            removeLine() {
               var order = this.env.pos.get_order();
              var lines = order.get_orderlines();
                for (const line of lines) {
                   if (this.env.pos.config.healthy_fdiscount_product_id[0]==line.product.id || this.env.pos.config.healthy_pdiscount_product_id[0]==line.product.id ){
                   line.set_quantity("remove");
                   }

                }
                this.props.line.set_quantity("remove");

            }

        };
    Registries.Component.extend(Orderline, PosOrderline);
    return Orderline;
});
