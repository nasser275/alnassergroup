odoo.define('aspl_pos_create_so_extension.CreateSaleOrderButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { Gui } = require('point_of_sale.Gui');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const { posbus } = require('point_of_sale.utils');

    class CreateSaleOrderButton extends PosComponent {
        constructor(){
            super(...arguments);
            useListener('click', this.onClick);
        }
        async onClick(){
            if(!this.env.pos.get_client()){
                confirm('Please Select Customer!');
                return;
            }
            if(this.env.pos.get_order().get_orderlines().length == 0){
                 confirm('Please Select Product!');
                 return;
            }
            this.showScreen('CreateSaleOrderScreen');
        }
    }

    CreateSaleOrderButton.template = 'CreateSaleOrderButton';

    ProductScreen.addControlButton({
        component: CreateSaleOrderButton,
        condition: function(){
            return this.props.SoMode;
        },
    });

    Registries.Component.add(CreateSaleOrderButton);

    return CreateSaleOrderButton;
});
