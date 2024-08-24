odoo.define('pos_delivery_service.delivery_service_pop', function (require) {
    "use strict";


    var rpc = require('web.rpc');
    const Registries = require('point_of_sale.Registries');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const {Gui} = require('point_of_sale.Gui');
    const ajax = require('web.ajax');
    let core = require('web.core');
    let _t = core._t;


    const {
        useState,
        useRef
    } = owl.hooks;


    class DeliveryOrderWidget extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            this.state = useState({
                delivery_person_id: this.props.delivery_person_id,
                delivery_amount: this.props.delivery_amount,
                free_delivery: this.props.free_delivery,
            })


        }


        getPayload() {
            var selected_vals = [];
            var delivery_person_id = this.state.delivery_person_id;
            var delivery_amount = this.state.delivery_amount;
            var free_delivery = this.state.free_delivery;
            selected_vals.push(delivery_person_id);
            selected_vals.push(delivery_amount);
            selected_vals.push(free_delivery);
            return selected_vals
        }

        mounted() {


        }


        click_confirm() {
            var self = this;
            var payload = this.getPayload();
            var order = this.env.pos.get_order();
            if (!payload[0]) {
                self.showPopup('ErrorPopup', {
                    'title': _t('Unknown Delivery Person'),
                    'body': _t(' Select Delivery Person first.'),
                });
                return;
            }
            if (payload[1] > 100){
                self.showPopup('ErrorPopup', {
                    'title': _t('Delivery Amount Limit!'),
                    'body': _t('Delivery Limit Exceeds'),
                });
                return ;
            }


            order.delivery_person_id = payload[0];
            order.delivery_amount = payload[1];
            order.free_delivery = payload[2];
            order.is_delivery = true;
            self.add_delivery_amount(order.delivery_amount)
            order.do_coupon_operation()
            order.finalized=true
            this.env.pos.push_orders(order);
            this.showScreen('ProductScreen');
//            this.env.pos.add_new_order();
            this.showScreen('ReprintReceiptScreen', {order: order,is_delivery:true});
            alert("Order Created Draft!")
            self.trigger('close-popup');


        }

        add_delivery_amount(amount) {
            var order = this.env.pos.get_order();
            var lines = order.get_orderlines();
            var product = this.env.pos.db.get_product_by_id(this.env.pos.config.delivery_service_product_id[0]);

            // Remove existing discounts
            var i = 0;
            while (i < lines.length) {
                if (lines[i].get_product() === product) {
                    order.remove_orderline(lines[i]);
                } else {
                    i++;
                }
            }
            order.add_product(product, {price: amount});
        }


    }

    DeliveryOrderWidget.template = 'DeliveryOrderWidget';
    DeliveryOrderWidget.defaultProps = {
        confirmText: 'Create',
        cancelText: 'Cancel',
        title: 'Create Delivery Order',
        body: '',
    };

    Registries.Component.add(DeliveryOrderWidget);
    return DeliveryOrderWidget;


});