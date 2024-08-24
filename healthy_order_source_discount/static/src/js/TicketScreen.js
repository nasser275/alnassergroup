odoo.define('healthy_order_source_discount.TicketScreen', function (require) {
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
                    _getSearchFields() {
                const fields = {
                    RECEIPT_NUMBER: {
                        repr: (order) => order.name,
                        displayName: this.env._t('Receipt Number'),
                        modelField: 'pos_reference',
                    },
                    IS_DELIVERY: {
                        repr: (order) => order.delivery,
                        displayName: this.env._t('DELIVERY'),
                        modelField: 'delivery',
                    },
                    DATE: {
                        repr: (order) => moment(order.creation_date).format('YYYY-MM-DD hh:mm A'),
                        displayName: this.env._t('Date'),
                        modelField: 'date_order',
                    },
                    CUSTOMER: {
                        repr: (order) => order.get_client_name(),
                        displayName: this.env._t('Customer'),
                        modelField: 'partner_id.display_name',
                    },
                };

                if (this.showCardholderName()) {
                    fields.CARDHOLDER_NAME = {
                        repr: (order) => order.get_cardholder_name(),
                        displayName: this.env._t('Cardholder Name'),
                        modelField: 'payment_ids.cardholder_name',
                    };
                }

                return fields;
            }

            async _onDoRefund() {
                const order = this.getSelectedSyncedOrder();
                if (!order) {
                    this._state.ui.highlightHeaderNote = !this._state.ui.highlightHeaderNote;
                    return this.render();
                }

                if (this._doesOrderHaveSoleItem(order)) {
                    this._prepareAutoRefundOnOrder(order);
                }

                const customer = order.get_client();

                // Select the lines from toRefundLines (can come from different orders)
                // such that:
                //   - the quantity to refund is not zero
                //   - if there is customer in the selected paid order, select the items
                //     with the same orderPartnerId
                //   - it is not yet linked to an active order (no destinationOrderUid)
                const allToRefundDetails = Object.values(this.env.pos.toRefundLines).filter(
                    ({qty, orderline, destinationOrderUid}) =>
                        !this.env.pos.isProductQtyZero(qty) &&
                        (customer ? orderline.orderPartnerId == customer.id : true) &&
                        !destinationOrderUid
                );
                if (allToRefundDetails.length == 0) {
                    this._state.ui.highlightHeaderNote = !this._state.ui.highlightHeaderNote;
                    return this.render();
                }

                // The order that will contain the refund orderlines.
                // Use the destinationOrder from props if the order to refund has the same
                // customer as the destinationOrder.
                const destinationOrder =
                    this.props.destinationOrder && customer === this.props.destinationOrder.get_client()
                        ? this.props.destinationOrder
                        : this.env.pos.add_new_order({silent: true});

                // Add orderline for each toRefundDetail to the destinationOrder.
                for (const refundDetail of allToRefundDetails) {
                    const {qty, orderline} = refundDetail;
                    await destinationOrder.add_product(this.env.pos.db.get_product_by_id(orderline.productId), {
                        quantity: -qty,
                        price: orderline.price,
                        lst_price: orderline.price,
                        extras: {price_manually_set: true},
                        merge: false,
                        refunded_orderline_id: orderline.id,
                        tax_ids: orderline.tax_ids,
                        discount: orderline.discount,
                    });
                    refundDetail.destinationOrderUid = destinationOrder.uid;
                }

                // Set the customer to the destinationOrder.
                if (customer && !destinationOrder.get_client()) {
                    destinationOrder.set_client(customer);
                }
                if (order.order_source_id){
                    destinationOrder.order_source_id=order.order_source_id
                }
                if (order.discount_type){
                    destinationOrder.discount_type=order.discount_type
                }

                if (order.discount_by){
                    destinationOrder.discount_by=order.discount_by
                }

                if (order.discount_code){
                    destinationOrder.discount_code=order.discount_code
                }
                 if (order.discount_reason_id){
                    destinationOrder.discount_reason_id=order.discount_reason_id
                }
                  if (order.discount_offer_id){
                    destinationOrder.discount_offer_id=order.discount_offer_id
                }
                   if (order.sales_person){
                    destinationOrder.sales_person=order.sales_person
                }




                this._onCloseScreen();
            }


        };

    Registries.Component.extend(TicketScreen, PosResTicketScreen);

    return {TicketScreen};
});
