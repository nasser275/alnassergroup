odoo.define('healthy_salesperson.pos_custom3', function (require) {
    "use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const {Gui} = require('point_of_sale.Gui');
    const L10nCoPosPaymentScreen = PaymentScreen =>
        class extends PaymentScreen {
            async _isOrderValid(isForceValidate) {
                var order = this.env.pos.get_order();
                if (this.env.pos.config.show_sales_represtiative){
                     if (!order.sales_person) {
                    const {confirmed} = await this.showPopup('ConfirmPopup', {
                        title: this.env._t('Please select Sales Represtiative'),
                        body: this.env._t(
                            'You need to select  Sales Represtiative  before you can invoice or ship an order.'
                        ),
                    });
                    if (confirmed) {
                         Gui.showPopup('POSSalesPersonPopup');
                    }
                    return false;
                }
                }


                return super._isOrderValid(...arguments);


            }
        };

    Registries.Component.extend(PaymentScreen, L10nCoPosPaymentScreen);

    return PaymentScreen;






});
