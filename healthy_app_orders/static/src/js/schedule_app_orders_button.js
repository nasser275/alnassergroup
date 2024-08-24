odoo.define('healthy_app_orders.schedule_app_orders_button', function (require) {
    "use strict";

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const {useListener} = require('web.custom_hooks');
    const {Gui} = require('point_of_sale.Gui');


    class ScheduleAppOrderButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.button_click);
        }

        button_click() {
            var self = this;
            var order = this.env.pos.get_order();
            var partner_id = false;
            var orderlines = order.orderlines.models;
            if (order.get_client() != null)
                partner_id = order.get_client();
            if (!partner_id) {
                self.selectClient();
            } else if (orderlines.length < 1) {
                 return this.showPopup('ErrorPopup', {
                    'title': 'Empty Order',
                    'body': 'Please select some products',
                });
                return false;
            } else {
                Gui.showPopup('ScheduleAppOrderPopupWidget', {
                    'title': ('Schedule App Order'),
                    'app_order_id': order.app_order_id,
                });
            }
        }
    }

    ScheduleAppOrderButton.template = 'ScheduleAppOrderButton';
    ProductScreen.addControlButton({
        component: ScheduleAppOrderButton,
        condition: function () {
            return true;
        },
        position: ['before', 'SetPricelistButton'],
    });

    Registries.Component.add(ScheduleAppOrderButton);
    return ScheduleAppOrderButton;
});