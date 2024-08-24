odoo.define('point_of_sale.AttachmentsWidget', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useState, useRef } = owl.hooks;
    const { useListener } = require('web.custom_hooks');

    class AttachmentsWidget extends PosComponent {
        constructor() {
            super(...arguments);
        }

    }
    AttachmentsWidget.template = 'AttachmentsWidget';

    Registries.Component.add(AttachmentsWidget);

    return AttachmentsWidget;
});
