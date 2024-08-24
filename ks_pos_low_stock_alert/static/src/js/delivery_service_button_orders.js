odoo.define('pos_delivery_service.delivery_service_button_orders', function (require) {
    "use strict";
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const {useListener} = require('web.custom_hooks');
    const {Gui} = require('point_of_sale.Gui');
    let core = require('web.core');
    let _t = core._t;

    class DeliveryOrdersButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.button_click);
        }

        async button_click() {
            var self = this;
            self.link = window.location.origin + "/web#action=ks_pos_low_stock_alert.unpaid_pos_orders_action_view&view_type=list&model=pos.order";
            window.open(self.link, '_blank');

        }


    }


    DeliveryOrdersButton.template = 'DeliveryOrdersButton';
    ProductScreen.addControlButton({

        component: DeliveryOrdersButton,
        'condition': function () {
            return this.env.pos.config.enable_delivery_service;
        },
    });

    Registries.Component.add(DeliveryOrdersButton);

    return DeliveryOrdersButton;


});