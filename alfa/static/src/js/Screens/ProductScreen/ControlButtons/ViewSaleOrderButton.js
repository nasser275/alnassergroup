odoo.define('aspl_pos_create_so_extension.ViewSaleOrderButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { Gui } = require('point_of_sale.Gui');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class ViewSaleOrderButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        async onClick(){
            this.showScreen('SaleOrderScreen');
        }
    }

    ViewSaleOrderButton.template = 'ViewSaleOrderButton';

    ProductScreen.addControlButton({
        component: ViewSaleOrderButton,
        condition: function() {
            return this.props.SoMode;
        },
    });

    Registries.Component.add(ViewSaleOrderButton);

    return ViewSaleOrderButton;
});
