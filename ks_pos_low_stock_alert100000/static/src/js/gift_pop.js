odoo.define('pos_delivery_service.gift_pop', function (require) {
    "use strict";


    var rpc = require('web.rpc');
    const Registries = require('point_of_sale.Registries');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const {Gui} = require('point_of_sale.Gui');
    const ajax = require('web.ajax');
    let core = require('web.core');
    var QWeb = core.qweb;
    let _t = core._t;


    const {
        useState,
        useRef
    } = owl.hooks;


    class GiftPop extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);

            this.state = useState({
                gift_product: this.props.gift_product,
            })


        }


        getPayload() {
            var selected_vals = [];
            var gift_product = this.state.gift_product;
            selected_vals.push(gift_product);
            return selected_vals
        }

        mounted() {
        }

        _on_click_product(product) {
            var self = this;
            var product = self.env.pos.db.get_product_by_id(product.id);
            self.env.pos.get_order().add_product(product, {
                quantity: 1,
                is_gift: true,
                merge: false,
                discount: product.gift_discount || 100
            });
            var selected_line = self.env.pos.get_order().get_selected_orderline();
            selected_line.is_gift = true;
            $('#'+product.id).css("background-color", "green");
        }



    }

    GiftPop.template = 'GiftPop';
    GiftPop.defaultProps = {
        confirmText: 'Create',
        cancelText: 'Cancel',
        title: 'Gift',
        body: '',
    };

    Registries.Component.add(GiftPop);
    return GiftPop;


});