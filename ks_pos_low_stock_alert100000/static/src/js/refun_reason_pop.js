odoo.define('pos_delivery_service.refun_reason_pop', function (require) {
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


    class RefundReasonWidget extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);

            this.state = useState({
                return_reason: this.props.return_reason,
            })


        }


        getPayload() {
            var selected_vals = [];
            var return_reason = this.state.return_reason;
            selected_vals.push(return_reason);
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
                    'title': _t('Unknown Refund Reason'),
                    'body': _t(' Select Refund Reason'),
                });
                return;
            }
            order.return_reason = payload[0];
            self.trigger('close-popup');


        }



    }

    RefundReasonWidget.template = 'RefundReasonWidget';
    RefundReasonWidget.defaultProps = {
        confirmText: 'Select',
        cancelText: 'Cancel',
        title: 'Refund Reason',
        body: '',
    };

    Registries.Component.add(RefundReasonWidget);
    return RefundReasonWidget;


});