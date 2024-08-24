odoo.define('aspl_pos_combo.ticket', function (require) {
    'use strict';

    const TicketScreen = require('point_of_sale.TicketScreen');
    const Registries = require('point_of_sale.Registries');
    const {Gui} = require('point_of_sale.Gui');

    const TicketScreenExtended = (TicketScreen) =>
        class extends TicketScreen {
         getTotal(order) {
              var sum=0;
              var lines = order.get_orderlines();
               lines.forEach(function (line) {
                   if (line.main_combo==false && line.is_combo){
                   }else{

                       if (line)
                        sum+=line.get_price_with_tax()
                   }

               });
               return this.env.pos.format_currency( sum);
        }





        };

    Registries.Component.extend(TicketScreen, TicketScreenExtended);

    return TicketScreen;

});