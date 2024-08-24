odoo.define('app_list.AppOrderRow', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    /**
     * @props {models.Order} order
     * @props columns
     * @emits click-order
     */
    class AppOrderRow extends PosComponent {
        get order() {
            return this.props.order;
        }
        get highlighted() {
            const highlightedOrder = this.props.highlightedOrder;
            return !highlightedOrder ? false : highlightedOrder.backendId === this.props.order.backendId;
        }

        // Column getters //

        get name() {
            return this.order.name;
        }
        get date() {
            return moment(this.order.order_date).format('YYYY-MM-DD hh:mm A');
        }
        get customer() {
            const customer = this.order.partner_id;
            return customer ? customer[1] : null;
        }
        get total() {
            return this.env.pos.format_currency(this.order.amount_total);
        }
        get final_total() {
            return this.env.pos.format_currency(this.order.final_total);
        }
        get state() {
            let state_mapping = {
              'draft': this.env._t('Draft'),
              'received': this.env._t('Received'),
              'delivery': this.env._t('Delivery'),
              'payment': this.env._t('Payment'),
              'cancel': this.env._t('Cancelled'),
              'return': this.env._t('return'),
            };

            return state_mapping[this.order.state];
        }
        get salesman() {
            const salesman = this.order.sales_person;
            return salesman ? salesman[1] : null;
        }
        get branch() {
            const branch = this.order.branch_id;
            return branch ? branch[1] : null;
        }
        get order_source() {
            const order_source = this.order.order_source_id;
            return order_source ? order_source[1] : null;
        }
        get schedule_time() {
            return this.order.schedule_time;
        }
        get delivery_cost() {
            return this.order.delivery_cost;
        }
        get discount_type() {
            return this.order.discount_type;
        }
        get discount_value() {
            return this.order.discount;
        }
        get customer_notes() {
            return this.order.customer_notes;
        }
        get is_payment() {
            return this.order.is_paid;
        }

    }
    AppOrderRow.template = 'AppOrderRow';

    Registries.Component.add(AppOrderRow);

    return AppOrderRow;
});
