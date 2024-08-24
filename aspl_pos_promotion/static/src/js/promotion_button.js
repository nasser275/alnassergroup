odoo.define('aspl_pos_promotion.promotion_button', function (require) {
    "use strict";
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const {useListener} = require('web.custom_hooks');
    const {Gui} = require('point_of_sale.Gui');

    class POSPromotionProductsWidgetbutton extends PosComponent {

        constructor() {
            super(...arguments);
            useListener('click', this.button_click);
        }

        button_click() {
            var self = this;
            this.rpc({
                model: 'pos.promotion',
                method: 'get_available_combo',
                args: []
            }).then(function (products) {
                var prods = [];
                for (var i = 0; i < products.length; i++) {
                    if (self.env.pos.db.get_product_by_id(products[i])){
                        prods.push(self.env.pos.db.get_product_by_id(products[i]))
                    }

                }
                console.log(prods)
                 Gui.showPopup('PromotionWidget', {'products':prods});

            });
        }

    }


    POSPromotionProductsWidgetbutton.template = 'POSPromotionProductsWidgetbutton';
    ProductScreen.addControlButton({

        component: POSPromotionProductsWidgetbutton,
         condition: function () {
            return true;
        },
        position: ['before', 'SetPricelistButton'],
    });

    Registries.Component.add(POSPromotionProductsWidgetbutton);

    return POSPromotionProductsWidgetbutton;


});