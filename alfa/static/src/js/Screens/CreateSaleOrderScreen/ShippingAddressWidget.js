odoo.define('point_of_sale.ShippingAddressWidget', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useState, useRef } = owl.hooks;
    const { useListener } = require('web.custom_hooks');

    class ShippingAddressWidget extends PosComponent {
        constructor() {
            super(...arguments);
        }

    }
    ShippingAddressWidget.template = 'ShippingAddressWidget';

    Registries.Component.add(ShippingAddressWidget);

    return ShippingAddressWidget;
});
