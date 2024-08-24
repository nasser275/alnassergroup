odoo.define('pos_delivery_service.gift_button', function (require) {
    "use strict";
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const {useListener} = require('web.custom_hooks');
    const {Gui} = require('point_of_sale.Gui');
    let core = require('web.core');
    let _t = core._t;

    class GiftButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.button_click);
        }

        async button_click() {
            var self=this;
            var order = this.env.pos.get_order();
            if (!order.get_client()) {
                const {confirmed} = await this.showPopup('ConfirmPopup', {
                    title: this.env._t('Unknown customer'),
                    body: this.env._t(
                        'You cannot use Home Delivery. Select customer first.'
                    ),
                });
                if (confirmed) {
                    self.selectClient();
                }
                return;
            }
            var orderlines = order.orderlines.models;
            if (orderlines.length < 1) {
                this.showPopup('ErrorPopup', {
                    'title': _t('Empty Order !'),
                    'body': _t('Please select some products'),
                });
                return false;
            }
            Gui.showPopup('GiftPop');

        }
                async selectClient() {
        	var order = this.env.pos.get_order();
            // IMPROVEMENT: This code snippet is repeated multiple times.
            // Maybe it's better to create a function for it.
            const currentClient = order.get_client();
            const { confirmed, payload: newClient } = await this.showTempScreen(
                'ClientListScreen',
                { client: currentClient }
            );
            if (confirmed) {
                order.set_client(newClient);
                order.updatePricelist(newClient);
            }
        }



    }


    GiftButton.template = 'GiftButton';
    ProductScreen.addControlButton({

        component: GiftButton,
        'condition': function () {
            return this.env.pos.config.enable_gift;
        },
    });

    Registries.Component.add(GiftButton);

    return GiftButton;


});