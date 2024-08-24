odoo.define('hide_price_control.chrome_', function (require) {
    "use strict";

    const PosHrChrome = require('pos_hr.chrome');
        const Registries = require('point_of_sale.Registries');


    const CPosHrChrome = PosHrChrome =>
        class extends PosHrChrome {
           showCashMoveButton() {
               return this.env.pos && this.env.pos.config && this.env.pos.get('cashier').show_cash_in_out;
                }



        };

    Registries.Component.extend(PosHrChrome, CPosHrChrome);

    return PosHrChrome;


});
