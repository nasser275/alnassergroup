odoo.define('pos_delivery_service.ReprintReceiptScreen', function (require) {
    'use strict';

    const ReprintReceiptScreen = require('point_of_sale.ReprintReceiptScreen');
    const Registries = require('point_of_sale.Registries');

    const PosReprintReceiptScreenn = (ReprintReceiptScreen) =>
        class extends ReprintReceiptScreen {

         async printReceipt() {
                if(1==1) {
                    let result = await this._printReceipt();
                    // if(result)
                    //     this.showScreen('ProductScreen', );
                }
            }
         async new_order() {
                this.env.pos.add_new_order();
            }



        }

    Registries.Component.extend(ReprintReceiptScreen, PosReprintReceiptScreenn);

    return {ReprintReceiptScreen};
});
