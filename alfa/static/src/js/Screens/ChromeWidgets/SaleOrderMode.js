odoo.define('aspl_pos_create_so_extension.SaleOrderMode', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useState, useRef } = owl.hooks;


    class SaleOrderMode extends PosComponent {
        constructor() {
            super(...arguments);
        }
        async onClick(){
            this.trigger('toggle-mode')
        }
    }
    SaleOrderMode.template = 'SaleOrderMode';

    Registries.Component.add(SaleOrderMode);

    return SaleOrderMode;
});
