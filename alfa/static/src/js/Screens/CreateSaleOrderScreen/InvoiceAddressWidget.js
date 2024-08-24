odoo.define('point_of_sale.InvoiceAddressWidget', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useState, useRef } = owl.hooks;
    const { useListener } = require('web.custom_hooks');

    class InvoiceAddressWidget extends PosComponent {
        constructor() {
            super(...arguments);
        }

    }
    InvoiceAddressWidget.template = 'InvoiceAddressWidget';

    Registries.Component.add(InvoiceAddressWidget);

    return InvoiceAddressWidget;
});
