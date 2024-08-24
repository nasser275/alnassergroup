odoo.define('healthy_order_source_discount.order_source_button', function (require) {
    "use strict";
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const {useListener} = require('web.custom_hooks');
    const {Gui} = require('point_of_sale.Gui');

    class POSOrderSourceButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.button_click);
        }
        button_click() {
            var order = this.env.pos.get_order();
            if (order.app_order_id){
                    alert("Not Allow")
                }
            else {
                 Gui.showPopup('POSOrderSourcePopup', {
                'order_source_id': order.order_source_id, 'discount_code': order.discount_code,
            });
            }


        }


    }


    POSOrderSourceButton.template = 'POSOrderSourceButton';
    ProductScreen.addControlButton({

        component: POSOrderSourceButton,
        'condition': function () {
            return this.env.pos.config.show_order_source;
        },
    });

    Registries.Component.add(POSOrderSourceButton);

    return POSOrderSourceButton;


});