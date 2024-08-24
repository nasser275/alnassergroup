odoo.define('app_list.AppOrderManagementScreen', function (require) {
    'use strict';

    const {sprintf} = require('web.utils');
    const {parse} = require('web.field_utils');
    const {useContext} = owl.hooks;
    const {useListener} = require('web.custom_hooks');
    const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const Registries = require('point_of_sale.Registries');
    const AppOrderFetcher = require('app_list.AppOrderFetcher');
    const IndependentToOrderScreen = require('point_of_sale.IndependentToOrderScreen');
    const contexts = require('point_of_sale.PosContext');
    const models = require('point_of_sale.models');

    class AppOrderManagementScreen extends ControlButtonsMixin(IndependentToOrderScreen) {
        constructor() {
            super(...arguments);
            useListener('close-screen', this.close);
            useListener('click-app-order', this._onClickAppOrder);
            useListener('next-page', this._onNextPage);
            useListener('prev-page', this._onPrevPage);
            useListener('search', this._onSearch);

            AppOrderFetcher.setComponent(this);
            this.orderManagementContext = useContext(contexts.orderManagement);
        }

        mounted() {
            AppOrderFetcher.on('update', this, this.render);
            this.env.pos.get('orders').on('add remove', this.render, this);

            // calculate how many can fit in the screen.
            // It is based on the height of the header element.
            // So the result is only accurate if each row is just single line.
            const flexContainer = this.el.querySelector('.flex-container');
            const cpEl = this.el.querySelector('.control-panel');
            const headerEl = this.el.querySelector('.header-row');
            const val = Math.trunc(
                (flexContainer.offsetHeight - cpEl.offsetHeight - headerEl.offsetHeight) /
                headerEl.offsetHeight
            );
            console.log(">DD>>D",val)
            AppOrderFetcher.setNPerPage(val);

            // Fetch the order after mounting so that order management screen
            // is shown while fetching.
            setTimeout(() => AppOrderFetcher.fetch(), 0);
        }

        willUnmount() {
            AppOrderFetcher.off('update', this);
            this.env.pos.get('orders').off('add remove', null, this);
        }

        get selectedClient() {
            const order = this.orderManagementContext.selectedOrder;
            return order ? order.get_client() : null;
        }

        get orders() {
            return AppOrderFetcher.get();
        }

        async _setNumpadMode(event) {
            const {mode} = event.detail;
            this.numpadMode = mode;
            NumberBuffer.reset();
        }

        _onNextPage() {
            AppOrderFetcher.nextPage();
        }

        _onPrevPage() {
            AppOrderFetcher.prevPage();
        }

        _onSearch({detail: domain}) {
            AppOrderFetcher.setSearchDomain(domain);
            AppOrderFetcher.setPage(1);
            AppOrderFetcher.fetch();
        }

        async _onClickAppOrder(event) {
            const clickedOrder = event.detail;
            let currentPOSOrder = this.env.pos.get_order();
            currentPOSOrder.set_client(this.env.pos.db.get_partner_by_id(clickedOrder.partner_id[0]));
            currentPOSOrder.app_order_id = clickedOrder.id;
            currentPOSOrder.delivery_amount = clickedOrder.delivery_cost;
            currentPOSOrder.free_delivery = clickedOrder.free_delivery;
            if (clickedOrder.order_source_id) {
                currentPOSOrder.order_source_id = clickedOrder.order_source_id[0];
            }
            // if (clickedOrder.sales_person) {
            //     currentPOSOrder.delivery_person_id = clickedOrder.sales_person[0];
            // }
            var lines=await  this._getSOLines(clickedOrder.app_lines);
            for (const orderline of lines) {
                var product = this.env.pos.db.get_product_by_id(orderline.product_id[0]);
                    currentPOSOrder.add_product(product, {
                        price: orderline.price,
                        quantity: orderline.qty,
                        discount: orderline.discount,
                        merge: false,
                    });
                }
            // currentPOSOrder.trigger('change');
            console.log("D>D>D>",currentPOSOrder)
            this.close();

        }

        async _getSOLines(ids) {
            let so_lines = await this.rpc({
                model: 'app.order.lines',
                method: 'read_converted',
                args: [ids],
                context: this.env.session.user_context,
            });
            return so_lines;
        }

    }

    AppOrderManagementScreen.template = 'AppOrderManagementScreen';
    AppOrderManagementScreen.hideOrderSelector = true;

    Registries.Component.add(AppOrderManagementScreen);

    return AppOrderManagementScreen;
});
