odoo.define('healthy_order_source_discount.fixeddiscount_button', function (require) {
    "use strict";
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const {useListener} = require('web.custom_hooks');
    const {Gui} = require('point_of_sale.Gui');

    class FixedPOSDiscountButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.button_click);
        }
        button_click() {
            var order = this.env.pos.get_order();
            Gui.showPopup('HealthyNumberPopup'
            ,{
                'use':'f',
                'discount_type':"fixed",
                'discount_by':"offer",
                'discount_code':order.discount_code,
                'discount_reason_id':order.discount_reason_id,
                'discount_offer_id':order.discount_offer_id
            }
            );

        }


    }


    FixedPOSDiscountButton.template = 'FixedPOSDiscountButton';
    ProductScreen.addControlButton({

        component: FixedPOSDiscountButton,
        'condition': function () {
            return this.env.pos.config.enable_fdiscount;
        },
    });

    Registries.Component.add(FixedPOSDiscountButton);

    return FixedPOSDiscountButton;


});