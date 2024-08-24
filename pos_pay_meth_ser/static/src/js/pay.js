odoo.define('pos_pay_meth_ser.pos_pay', function(require) {
    "use strict";
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    var models = require('point_of_sale.models');
    models.load_fields('pos.payment.method', [
        'serial_number_required',

    ]);

    const L10nCoPosPaymentScreen = PaymentScreen =>
        class extends PaymentScreen {
            addNewPaymentLine({
                detail: paymentMethod
            }) {

                    var self = this;
                    var order = self.env.pos.get_order();
                    var serial_number_required = paymentMethod.serial_number_required;
                    if (serial_number_required) {
                        if ($('.pay_serial_no_input').val()) {} else {
                            this.showPopup('ErrorPopup', {
                                title: this.env._t('Error'),
                                body: this.env._t('Serial Number Required For This Payment Method'),
                            });
                            return false;
                        }



                    }


                    // original function: click_paymentmethods
                    let result = this.currentOrder.add_paymentline(paymentMethod);


                    if (result) {

                        NumberBuffer.reset();
                        result.transaction_id = $('.pay_serial_no_input').val()
                        order.payment_serial_no = $('.pay_serial_no_input').val()

                        return true;

                    } else {
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Error'),
                            body: this.env._t('There is already an electronic payment in progress.'),
                        });
                        return false;
                    }

            }

            async _isOrderValid(isForceValidate) {
                var order = this.env.pos.get_order();
                var serial_flag=false;
                var bank_flag=false;
                var min_flag=false;
                var total=0;
                if (order.paymentlines.models.length > 0) {
                       for (var i=0;i<order.paymentlines.models.length;i++){
                        console.log("D>>>F>F>F>F",order.paymentlines.models[i].payment_method.type)
                        total+=order.paymentlines.models[i].amount
                        if (order.paymentlines.models[i].payment_method.serial_number_required && !($('.pay_serial_no_input').val()) ) {
                         serial_flag=true;
                         break;
                        }
                        if (order.paymentlines.models[i].payment_method.type == 'bank') {
                        if (order.paymentlines.models[i].amount<0){
                         min_flag=true;
                          break;
                        }
                          bank_flag=true;
                           break;

                        }


                       }
                       console.log(">DD>D>>D",serial_flag,bank_flag,total)
                       if (serial_flag) {
                            this.showPopup('ErrorPopup', {
                                title: this.env._t('Error'),
                                body: this.env._t('Serial Number Required For This Payment Method'),
                            });
                            return false;

                        }
                    else if (min_flag) {
                            this.showPopup('ErrorPopup', {
                                title: this.env._t('Error'),
                                body: this.env._t('Paid Amount Must >0 '),
                            });
                            return false;

                    }
                    else if (bank_flag) {
                        if (parseInt(total) > parseInt(order.get_total_with_tax())) {
                            this.showPopup('ErrorPopup', {
                                title: this.env._t('Error'),
                                body: this.env._t('Paid Amount > Order Amount'),
                            });
                            return false;

                        }

                        else {
                            return super._isOrderValid(...arguments);

                        }
                    }
                     else {
                        return super._isOrderValid(...arguments);

                    }
                } else {
                    return super._isOrderValid(...arguments);
                }



            }



        };

    Registries.Component.extend(PaymentScreen, L10nCoPosPaymentScreen);

    return PaymentScreen;
});