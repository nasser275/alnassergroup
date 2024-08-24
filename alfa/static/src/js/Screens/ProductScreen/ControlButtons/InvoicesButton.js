odoo.define('aspl_pos_create_so_extension.InvoicesButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { Gui } = require('point_of_sale.Gui');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class InvoicesButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        async onClick(){
            this.showScreen('InvoiceScreen');
        }
    }

    InvoicesButton.template = 'InvoicesButton';

    ProductScreen.addControlButton({
        component: InvoicesButton,
        condition: function() {
            return this.env.pos.user.sale_order_invoice && this.props.SoMode;
        },
    });

    Registries.Component.add(InvoicesButton);

    return InvoicesButton;
});
