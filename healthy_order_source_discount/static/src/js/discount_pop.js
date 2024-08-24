odoo.define('healthy_order_source_discount.discount_pop', function (require) {
    "use strict";


    const Registries = require('point_of_sale.Registries');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const {
        useListener
    } = require('web.custom_hooks');

    const {
        useState,
        useRef
    } = owl.hooks;


    class HealthyNumberPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            useListener('accept-input', this.confirm);
            useListener('close-this-popup', this.cancel);
            let startingBuffer = '';
            if (typeof this.props.startingValue === 'number' && this.props.startingValue > 0) {
                startingBuffer = this.props.startingValue.toString();
            }
            this.state = useState({
                buffer: startingBuffer,
                toStartOver: this.props.isInputSelected,
                discount_type: this.props.discount_type,
                discount_by: this.props.discount_by,
                discount_code: this.props.discount_code,
                discount_reason_id: this.props.discount_reason_id,
                discount_offer_id: this.props.discount_offer_id,
                use: this.props.use,
            });
            NumberBuffer.use({
                nonKeyboardInputEvent: 'numpad-click-input',
                triggerAtEnter: 'accept-input',
                triggerAtEscape: 'close-this-popup',
                state: this.state,
            });

        }

        getPayload() {
            var selected_vals = [];
            var discount_type = this.state.discount_type;
            var discount_by = this.state.discount_by;
            var discount_code = this.state.discount_code;
            var discount_reason_id = this.state.discount_reason_id;
            var discount_offer_id = this.state.discount_offer_id;
            var use = this.state.use;
            selected_vals.push(discount_type);
            selected_vals.push(discount_by);
            selected_vals.push(discount_code);
            selected_vals.push(discount_reason_id);
            selected_vals.push(discount_offer_id);
            selected_vals.push(use);
            // return NumberBuffer.get();
            return selected_vals
        }

        mounted() {


        }


        click_confirm() {
            var self = this;
            var payload = this.getPayload();
            var order = this.env.pos.get_order();
             var discount_value = NumberBuffer.get();
             discount_value = Math.max(0, Math.min(10000, discount_value));
            if (order.orderlines.length < 1) {
                self.showPopup('ErrorPopup', {
                    'title': 'Empty Order !',
                    'body': 'Please select some products',
                });
                return false;
            }
            if (discount_value > order.get_total_with_tax()) {
                return this.showPopup('ErrorPopup', {
                    'title': 'Discount Error',
                    'body': 'Discount > Total Of Order',
                });
                return false;
            }

            if (payload[0] && payload[1]) {
                if (payload[1] == 'code') {
                    if (payload[3]) {}else {
                       return self.showPopup('ErrorPopup', {
                            title: self.env._t('Unknown Discount Reason'),
                            body: self.env._t("Select Discount Reason!"),
                        });
                    }
                    if (payload[2]) {}else{
                        return self.showPopup('ErrorPopup', {
                            title: self.env._t('Unknown Discount Code'),
                            body: self.env._t("Add Discount Code!"),
                        });
                    }
                }
                if (payload[1] == 'offer') {
                    if (payload[4]) {
                        console.log(">D>>F>33",)
                    }else {
                         console.log(">D>>F>33",)
                        return self.showPopup('ErrorPopup', {
                            title: self.env._t('Unknown Discount Offer'),
                            body: self.env._t("Select Discount Offer!"),
                        });
                    }
                }
                order.discount_type = payload[0];
                order.discount_by = payload[1];
                order.discount_code = payload[2];
                order.discount_reason_id = payload[3];
                order.discount_offer_id = payload[4];
                                   console.log(">D>>F>1",payload,payload[5])

                if (payload[5]=='p'){
                  if(order.get_total_with_tax()>=this.env.pos.config.perc_min_order_total){
                if (discount_value>this.env.pos.config.perc_max_order_total){
                 return self.showPopup('ErrorPopup', {
                            title: self.env._t('Max Discount Value'),
                            body: self.env._t("Max Discount "+this.env.pos.config.perc_max_order_total.toString()),
                        });
                }else{
                  this.apply_discount_fixed(discount_value, payload[0],payload[5]);
                }

                }else{
                 return self.showPopup('ErrorPopup', {
                            title: self.env._t('Minimum Order Total'),
                            body: self.env._t("Minimum Order Total "+this.env.pos.config.perc_min_order_total.toString()),
                        });
                }



                }
                else if (payload[5]=='f'){
                  if(order.get_total_with_tax()>=this.env.pos.config.fixed_min_order_total){
                if (discount_value>this.env.pos.config.fixed_max_order_total){
                 return self.showPopup('ErrorPopup', {
                            title: self.env._t('Max Discount Value'),
                            body: self.env._t("Max Discount "+this.env.pos.config.fixed_max_order_total.toString()),
                        });
                }else{
                  this.apply_discount_fixed(discount_value, payload[0],payload[5]);
                }

                }else{
                 return self.showPopup('ErrorPopup', {
                            title: self.env._t('Minimum Order Total'),
                            body: self.env._t("Minimum Order Total "+this.env.pos.config.fixed_min_order_total.toString()),
                        });
                }
                }
                else{
                this.apply_discount_fixed(discount_value, payload[0],payload[5]);
                }


            } else {
                return self.showPopup('ErrorPopup', {
                            title: self.env._t('Unknown Discount Type Or  Discount By '),
                            body: self.env._t("Select Discount Type Or Discount By !"),
                        });
            }


            this.trigger('close-popup');


        }


        get decimalSeparator() {
            return this.env._t.database.parameters.decimal_point;
        }

        get inputBuffer() {
            if (this.state.buffer === null) {
                return '';
            }
            if (this.props.isPassword) {
                return this.state.buffer.replace(/./g, '•');
            } else {
                return this.state.buffer;
            }
        }

        sendInput(key) {
            this.trigger('numpad-click-input', {
                key
            });
        }

        apply_discount_fixed(pc, type,use) {
            var order = this.env.pos.get_order();
            var lines = order.get_orderlines();
            if (use=='f'){
                var product = this.env.pos.db.get_product_by_id(this.env.pos.config.healthy_fdiscount_product_id[0]);
            }
            if (use=='p'){
                var product = this.env.pos.db.get_product_by_id(this.env.pos.config.healthy_pdiscount_product_id[0]);
            }
            if (use=='ap'){
                var product = this.env.pos.db.get_product_by_id(this.get_disc_product(order.discount_reason_id))
            }

            // Remove existing discounts
            var i = 0;
            while (i < lines.length) {
                if (lines[i].get_product() === product) {
                    order.remove_orderline(lines[i]);
                } else {
                    i++;
                }
            }

            // Add discount
            if (type == 'fixed') {
                var discount = -pc;
            } else {
                var discount = -pc / 100.0 * order.get_total_with_tax();
            }


            if (discount < 0) {
                order.add_product(product, {price: discount, lst_price: discount,
                    extras: {
                        price_manually_set: true,
                    },});
            }
        }

        get_disc_product(app_id) {
            var reasons = this.env.pos.reasons;
            for (var i = 0; i < reasons.length; i++) {
                if (reasons[i].id == app_id) {
                    console.log("reasons[i]", reasons[i].healthy_discount_product_id[0])
                    return reasons[i].healthy_discount_product_id[0]
                }

            }
        }


    }

    HealthyNumberPopup.template = 'HealthyNumberPopup';
    HealthyNumberPopup.defaultProps = {
        confirmText: 'Apply',
        cancelText: 'Cancel',
        title: 'Healthy Discounts',
        body: '',
    };

    Registries.Component.add(HealthyNumberPopup);
    return HealthyNumberPopup;


});