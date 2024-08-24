odoo.define('almoasher_pos_coupons.coupons_button', function (require) {
    "use strict";
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const {useListener} = require('web.custom_hooks');
    const {Gui} = require('point_of_sale.Gui');

    function get_coupon_product(products) {
        for (var i in products) {
            if (products[i]['display_name'] == 'POS-Coupon-Product')
                return products[i]['id'];
        }
        return false;
    }

    class POSCouponWidgetbutton extends PosComponent {

        constructor() {
            super(...arguments);
            useListener('click', this.button_click);
        }

        button_click() {
            var self = this;
            var order = this.env.pos.get_order();
            var client = order.get_client()
            // console.log('order ==============> ', order, order.coupon);
            if (!self.coupon_product)
                self.coupon_product = get_coupon_product(this.env.pos.db.product_by_id);
            self.env.pos.refresh_coupons_data()
            if (!client) {
                this.trigger('click-customer')
            } else if (!self.coupon_product) {
                self.trigger('close-popup');
                self.showPopup('ErrorPopup', { title: "Can not find coupoun product!", body: "Coupon product name (POS-Coupon-Product) doesn't appear on pos"});
            } else {
                if (order.coupon) {
                    self.trigger('close-popup');
                    self.showPopup('ErrorPopup', { title: "Order has coupon !", body: "This order already has coupon and waiting for finish it."});
                } else {
                    setTimeout(function () {
                         Gui.showPopup('POSCouponPopupWidget');
                    }, 400);
                }
                // }
            }
        }


    }


    POSCouponWidgetbutton.template = 'POSCouponWidgetbutton';
    ProductScreen.addControlButton({

        component: POSCouponWidgetbutton,
        'condition': function () {
            return this.env.pos.config.show_coupon;
        },
        position: ['before', 'SetPricelistButton'],
    });

    Registries.Component.add(POSCouponWidgetbutton);

    return POSCouponWidgetbutton;


});