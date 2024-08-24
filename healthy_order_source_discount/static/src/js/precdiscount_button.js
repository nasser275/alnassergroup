odoo.define('healthy_order_source_discount.precdiscount_button', function (require) {
    "use strict";
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const {useListener} = require('web.custom_hooks');
    const {Gui} = require('point_of_sale.Gui');

    class PerPOSDiscountButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.button_click);
        }
        button_click() {
            var order = this.env.pos.get_order();
            Gui.showPopup('HealthyNumberPopup'
            ,{
                'use':'p',
                'discount_type':"percentage",
                'discount_by':"offer",
                'discount_code':order.discount_code,
                'discount_reason_id':order.discount_reason_id,
                'discount_offer_id':order.discount_offer_id
            }
            );

        }


    }


    PerPOSDiscountButton.template = 'PerPOSDiscountButton';
    ProductScreen.addControlButton({

        component: PerPOSDiscountButton,
        'condition': function () {
            return this.env.pos.config.enable_pdiscount;
        },
    });

    Registries.Component.add(PerPOSDiscountButton);

    return PerPOSDiscountButton;


});