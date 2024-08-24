odoo.define('pos_delivery_service.pos_custom222', function (require) {
    "use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const {Gui} = require('point_of_sale.Gui');
    const L10nCoPosPaymentScreen = PaymentScreen =>
        class extends PaymentScreen {
            async _isOrderValid(isForceValidate) {
                var order = this.env.pos.get_order();
                // console.log("orderaaaaaaaa",)
                if (!order.return_reason && order.getHasRefundLines()) {
                    const {confirmed} = await this.showPopup('ConfirmPopup', {
                        title: this.env._t('Please select  Refund Reason'),
                        body: this.env._t(
                            'You need to select  Refund Reason  before you can invoice or ship an order.'
                        ),
                    });
                    if (confirmed) {
                         Gui.showPopup('RefundReasonWidget');
                    }
                    return false;
                }
                return super._isOrderValid(...arguments);


            }
        };

    Registries.Component.extend(PaymentScreen, L10nCoPosPaymentScreen);

    return PaymentScreen;






});
