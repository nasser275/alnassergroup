odoo.define('hide_price_control.TicketScreen', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const TicketScreen = require('point_of_sale.TicketScreen');
    const Registries = require('point_of_sale.Registries');
    const {useAutofocus} = require('web.custom_hooks');
    const {posbus} = require('point_of_sale.utils');
    const {parse} = require('web.field_utils');
    const {useState, useContext} = owl.hooks;
    const PosResTicketScreen = (TicketScreen) =>
        class extends TicketScreen {

        _getRefundableDetails(customer) {
            return Object.values(this.env.pos.toRefundLines).filter(
                ({ qty, orderline, destinationOrderUid }) =>
                    !this.env.pos.isProductQtyZero(qty) &&
                    (customer ? orderline.orderPartnerId == customer.id : true) &&
                    !destinationOrderUid
            );
        }

        _setDestinationOrder(order, customer) {
            if(order && customer === order.get_client() && !this.env.pos.doNotAllowRefundAndSales())
                return order;
            else if(this.env.pos.get_order() && !this.env.pos.get_order().orderlines.length)
                return this.env.pos.get_order();
            else
                return this.env.pos.add_new_order({ silent: true });
        }
          _prepareRefundOrderlineOptions(toRefundDetail) {
            const { qty, orderline } = toRefundDetail;
            return {
                quantity: -qty,
                price: orderline.price,
                extras: { price_manually_set: true },
                merge: false,
                refunded_orderline_id: orderline.id,
                tax_ids: orderline.tax_ids,
                discount: orderline.discount,
            }
        }
        _onCloseScreen() {
         var order = this.env.pos.get_order();
         if (order,order.is_delivery){
          this.env.pos.add_new_order();
         }
            this.close();
        }


        async do_rufund() {
            const order = this.getSelectedSyncedOrder();
            if (!order) {
                this._state.ui.highlightHeaderNote = !this._state.ui.highlightHeaderNote;
                return this.render();
            }

            if (this._doesOrderHaveSoleItem(order)) {
                this._prepareAutoRefundOnOrder(order);
            }

            const customer = order.get_client();

            const allToRefundDetails = this._getRefundableDetails(customer)
            if (allToRefundDetails.length == 0) {
                this._state.ui.highlightHeaderNote = !this._state.ui.highlightHeaderNote;
                return this.render();
            }

            // The order that will contain the refund orderlines.
            // Use the destinationOrder from props if the order to refund has the same
            // customer as the destinationOrder.
            const destinationOrder = this._setDestinationOrder(this.props.destinationOrder, customer);
            console.log(">>D>YYYSYSYSSYYD>",order,order.order_source_id)
            destinationOrder.order_source_id=order.order_source_id
            // Add orderline for each toRefundDetail to the destinationOrder.
            for (const refundDetail of allToRefundDetails) {
                const product = this.env.pos.db.get_product_by_id(refundDetail.orderline.productId);
                const options = this._prepareRefundOrderlineOptions(refundDetail);
                await destinationOrder.add_product(product, options);
                refundDetail.destinationOrderUid = destinationOrder.uid;
            }

            // Set the customer to the destinationOrder.
            if (customer && !destinationOrder.get_client()) {
                destinationOrder.set_client(customer);
                destinationOrder.updatePricelist(customer);
            }

            this._onCloseScreen();
        }


            async _onDoRefund() {
                const old_order = this.getSelectedSyncedOrder();

                const employee = this.env.pos.get_cashier();
                if (employee.use_pos_password) {
                    var result = await this.askPin(employee.user_password);
                    if (result) {
                       this.do_rufund()
                    }
                }else{
                    return this.showPopup('ErrorPopup', {
                            title: ('Unknown User'),
                            body: ("Not Allow!"),
                        });
                }
            }
            async  askPin(pin) {
            const { confirmed, payload: inputPin } = await this.showPopup('NumberPopup', {
                isPassword: true,
                title: this.env._t('Password ?'),
                startingValue: null,
            });

            if (!confirmed) return false;
            console.log("pin",pin,inputPin)
            if (pin === inputPin) {
                return true;
            } else {
                await this.showPopup('ErrorPopup', {
                    title: this.env._t('Incorrect Password'),
                });
                return false;
            }
        }


        };

    Registries.Component.extend(TicketScreen, PosResTicketScreen);

    return {TicketScreen};
});
