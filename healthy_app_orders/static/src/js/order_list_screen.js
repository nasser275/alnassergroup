odoo.define('healthy_app_orders.order_list_screen', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var gui = require('point_of_sale.Gui');
    var core = require('web.core');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');
    var _t = require('web.core')._t;
    var session = require('web.session');
    const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const {onChangeOrder, useBarcodeReader} = require('point_of_sale.custom_hooks');
    const {useState, useRef} = owl.hooks;
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const {useListener} = require('web.custom_hooks');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const IndependentToOrderScreen = require('point_of_sale.IndependentToOrderScreen');
    const {posbus} = require('point_of_sale.utils');
    const {Gui} = require('point_of_sale.Gui');


    class OrderListScreenWidget extends IndependentToOrderScreen {
        constructor() {
            super(...arguments);
            useListener('filter-selected', this._onFilterSelected);
            useListener('search', this._onSearch);
            this.searchDetails = {};
            this.filter = null;
            this._initializeSearchFieldConstants();
        }

        mounted() {
            var self = this;
            this.render();
            var orders = this.env.pos.orders;
            var search_timeout = null;
        }

        back() {
            this.close();
        }

        reload() {
            window.location.reload(false);
        }

        create_order_click(order) {
            this.create_order(order);
        }

        get ordersList() {
            const filterCheck = (order) => {
                return true;
            };
            const {fieldName, searchTerm} = this.searchDetails;
            const searchField = this._searchFields[fieldName];
            const searchCheck = (order) => {
                if (!searchField) return true;
                const repr = searchField.repr(order);
                if (repr === null) return true;
                if (!searchTerm) return true;
                return repr && repr.toString().toLowerCase().includes(searchTerm.toLowerCase());
            };
            const predicate = (order) => {
                return filterCheck(order) && searchCheck(order);
            };

            return this.orderList.filter(predicate);
        }

        _onFilterSelected(event) {
            this.filter = event.detail.filter;
            this.render();
        }

        get orderList() {
            return this.env.pos.orders;
        }

        get _searchFields() {
            const fields = {

                RECEIPT_NUMBER: {
                    repr: (order) => order.name,
                    displayName: this.env._t('APP Order Number'),
                    modelField: 'name',
                },


            };
            return fields;
        }

        _onSearch(event) {
            const searchDetails = event.detail;
            Object.assign(this.searchDetails, searchDetails);
            this.render();
        }

        get searchBarConfig() {
            return {
                searchFields: new Map(
                    Object.entries(this._searchFields).map(([key, val]) => [key, val.displayName])
                ),
                filter: {show: true, options: this.filterOptions},
                defaultSearchDetails: this.searchDetails,
            };
        }

        get filterOptions() {
            const orderStates = this._getOrderStates();
            return orderStates;
        }

        _getOrderStates() {
            const states = new Map();
            states.set('All Orders', {
                text: this.env._t('All Orders'),
            });
            return states;
        }

        getStatus(order) {
            const screen = order.get_screen_data();
            return this._getOrderStates().get(this.__screenToStatusMap[screen.name]).text;

        }

        get _screenToStatusMap() {
            return {};
        }

        _initializeSearchFieldConstants() {
            this.constants = {};
            Object.assign(this.constants, {
                searchFieldNames: Object.keys(this._searchFields),
                screenToStatusMap: this._screenToStatusMap,
            });
        }

        render_list(orders) {
            var contents = this.el.querySelector('.order-list-contents');
            contents.innerHTML = "";
            for (var i = 0, len = Math.min(orders.length, 1000); i < len; i++) {
                var order = orders[i];
                var orderline_html = this.env.qweb.render('OrderLine', {widget: this, order: order});
                var orderline = document.createElement('tbody');
                orderline.innerHTML = orderline_html;
                orderline = orderline.childNodes[1];
                contents.appendChild(orderline);
            }
        }

        create_order(order_id) {
            var self = this;
            if (order_id.state == 'draft') {
                var current_order = self.env.pos.add_new_order();
                for (const orderline of order_id.app_lines) {
                    var line = self.get_app_line(orderline)
                    var product = this.env.pos.db.get_product_by_id(line.product_id[0]);
                    current_order.add_product(product, {
                        price: line.price,
                        quantity: line.qty,
                        discount: line.discount,
                        merge: false,
                    });
                }
                current_order.app_order_id = order_id.id;
                current_order.delivery_amount = order_id.delivery_cost;
                current_order.free_delivery = order_id.free_delivery;
                if (order_id.sales_person){
                    current_order.delivery_person_id = order_id.sales_person[0];
                }
                current_order.set_client(self.env.pos.db.get_partner_by_id(order_id.partner_id[0]))
                self.showScreen('ProductScreen');
            }
        }

        get_app_line(line_id) {
            for (var i = 0; i < this.env.pos.order_lines.length; ++i) {
                if (this.env.pos.order_lines[i].id == line_id) {
                    return this.env.pos.order_lines[i]
                }

            }


        }

    }

    OrderListScreenWidget.template = 'OrderListScreenWidget';

    Registries.Component.add(OrderListScreenWidget);

    return OrderListScreenWidget;

});