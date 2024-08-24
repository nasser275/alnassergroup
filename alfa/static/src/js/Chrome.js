odoo.define('aspl_pos_create_so_extension.chrome', function (require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const Chrome = require('point_of_sale.Chrome');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');

    const ChromeInherit = (Chrome) => class extends Chrome {
        constructor() {
            super(...arguments);
            useListener('toggle-mode', this.ToggleSo);
            this.state.SaleOrderMode = true;
        }
        async ToggleSo(){
            this.state.SaleOrderMode = !this.state.SaleOrderMode;
            this.env.pos.get_order().set_sale_order_mode(this.state.SaleOrderMode);
            this.render();
        }
    }
    Registries.Component.extend(Chrome, ChromeInherit);

    return Chrome;
});
