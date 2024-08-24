odoo.define('healthy_order_source_discount.order_source_pop', function (require) {
    "use strict";


    var rpc = require('web.rpc');
    var _t = require('web.core')._t;
    const Registries = require('point_of_sale.Registries');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const {Gui} = require('point_of_sale.Gui');
    const ajax = require('web.ajax');

    const {
        useState,
        useRef
    } = owl.hooks;


    class POSOrderSourcePopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);

            this.state = useState({
                order_source_id: this.props.order_source_id,
                discount_reason_id: this.props.discount_reason_id,
                discount_code: this.props.discount_code,
            })


        }


        getPayload() {
            var selected_vals = [];
            var order_source_id = this.state.order_source_id;
            var discount_reason_id = this.state.discount_reason_id;
            var discount_code = this.state.discount_code;
            selected_vals.push(order_source_id);
            selected_vals.push(discount_reason_id);
            selected_vals.push(discount_code);
            return selected_vals
        }

        mounted() {


        }


        click_confirm() {
            var self = this;
            var payload = this.getPayload();
            var order = this.env.pos.get_order();
            console.log("D>D>", self.get_remove_promotion(payload[0]))
            if (self.get_remove_promotion(payload[0])) {
                self.remove_promotion();
            }
            order.order_source_id = payload[0];
            order.discount_reason_id = payload[1];
            order.discount_code = payload[2];
            order.discount_by = "code";

            self.trigger('close-popup');


        }

        remove_promotion() {
            var order = this.env.pos.get_order();
            var lines = order.get_orderlines();
            lines.forEach(function (line) {
                line.set_promotion(false);
                line.set_rule(false, 0);
                line.is_promotion = false;
                line.discount = 0;
            });

        }

        get_remove_promotion(source) {
            var sources = this.env.pos.sources;
            for (var i = 0; i < sources.length; i++) {
                if (sources[i].id == source) {
                    return sources[i].remove_promotion;
                }

            }
        }


    }

    POSOrderSourcePopup.template = 'POSOrderSourcePopup';
    POSOrderSourcePopup.defaultProps = {
        confirmText: 'Select',
        cancelText: 'Cancel',
        title: 'Set Order Source',
        body: '',
    };

    Registries.Component.add(POSOrderSourcePopup);
    return POSOrderSourcePopup;


});