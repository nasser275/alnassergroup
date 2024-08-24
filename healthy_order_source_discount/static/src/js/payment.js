odoo.define('healthy_order_source_discount.pos_custom2', function (require) {
    "use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const {Gui} = require('point_of_sale.Gui');
    const L10nCoPosPaymentScreen = PaymentScreen =>
        class extends PaymentScreen {
            async _isOrderValid(isForceValidate) {
                if (this.env.pos.config.customer_required){
                if (!this.currentOrder.get_client()) {
                const { confirmed } = await this.showPopup('ConfirmPopup', {
                    title: this.env._t('Please select the Customer'),
                    body: this.env._t(
                        'You need to select the customer before you can invoice or ship an order.'
                    ),
                });
                if (confirmed) {
                    this.selectClient();
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
