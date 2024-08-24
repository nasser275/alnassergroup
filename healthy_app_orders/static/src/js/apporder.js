odoo.define('healthy_app_orders.apporder', function (require) {
    "use strict";

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const {useListener} = require('web.custom_hooks');


    class APPOrderButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.button_click);
        }

        button_click() {
            var orders = this.env.pos.orders;
            this.showScreen('OrderListScreenWidget', {orders: orders});
        }
    }

    APPOrderButton.template = 'APPOrderButton';
    ProductScreen.addControlButton({
        component: APPOrderButton,
        condition: function () {
            return true;
        },
        position: ['before', 'SetPricelistButton'],
    });

    Registries.Component.add(APPOrderButton);
    return APPOrderButton;
});