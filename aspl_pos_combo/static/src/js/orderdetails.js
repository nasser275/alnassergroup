odoo.define('aspl_pos_combo.OrderDetails', function (require) {
    'use strict';

    const OrderDetails = require('point_of_sale.OrderDetails');
    const Registries = require('point_of_sale.Registries');

    const OrderDetailsExtended = (OrderDetails) =>
        class extends OrderDetails {
          get total() {
              var sum=0;
              var lines = this.order.get_orderlines();
               lines.forEach(function (line) {
                   if (line.main_combo==false && line.is_combo){

                   }else {
                       sum+=line.get_price_with_tax()
                   }
                   console.log("DD>DD>", line)

               });
            // return this.env.pos.format_currency(this.order ? this.order.get_total_without_tax()-this.order.get_total_discount(): 0);
            return this.env.pos.format_currency( sum);
        }
           get total_discount() {
            return this.env.pos.format_currency(this.order ? this.order.get_total_discount(): 0);
        }



        };

    Registries.Component.extend(OrderDetails, OrderDetailsExtended);

    return OrderWidget;

});