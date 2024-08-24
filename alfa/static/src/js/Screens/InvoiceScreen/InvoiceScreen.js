odoo.define('point_of_sale.InvoiceScreen', function(require) {
    'use strict';

    const IndependentToOrderScreen = require('point_of_sale.IndependentToOrderScreen');
    const Registries = require('point_of_sale.Registries');
    const { useState, useRef } = owl.hooks;
    const { useListener } = require('web.custom_hooks');
    var rpc = require('web.rpc');

    class InvoiceScreen extends IndependentToOrderScreen {
        constructor(){
            super(...arguments);
            this.filter = null;
            this.state = useState({ Invoices : ''})
            this.getInvoiceData();
            useListener('filter-selected', this._onFilterSelected);
            useListener('search', this._onSearch);
            this.searchDetails = {};
            this._initializeSearchFieldConstants();
        }
        _onFilterSelected(event){
            this.filter = event.detail.filter;
            this.render();
        }
        get Invoices() {
            return this.state.Invoices;
        }
        _onSearch(event) {
            const searchDetails = event.detail;
            Object.assign(this.searchDetails, searchDetails);
            this.render();
        }
        get searchBarConfig(){
            return {
                searchFields: this.constants.searchFieldNames,
                filter: { show: true, options: this.filterOptions },
            };
        }
        get filterOptions() {
            return ['All','Draft','Posted'];
        }
        get _searchFields() {
            var fields = {}
            fields = {
                'Name': (line) => line.name,
                'Due Date': (line) => line.invoice_date_due,
                'Date': (line) => line.date,
                'Customer': (line) => this.env.pos.db.get_partner_by_id(line.partner_id).name,
            };
            return fields;
        }
        get _screenToStatusMap() {
            return {
                draft : 'Draft',
                posted : 'Posted',
            };
        }
        _initializeSearchFieldConstants(){
            this.constants = {};
            Object.assign(this.constants, {
                searchFieldNames: Object.keys(this._searchFields),
                screenToStatusMap: this._screenToStatusMap,
            });
        }
        getInvoiceData(){
            this.state.Invoices = this.env.pos.db.get_invoices_list();
        }
        get filteredInvoiceList(){
            const filterCheck = (order) => {
                if(this.filter && this.filter !== 'All') {
                    const screen = order.state;
                    return this.filter === this.constants.screenToStatusMap[screen];
                }
                return true;
            };
            const { fieldValue, searchTerm } = this.searchDetails;
            const fieldAccessor = this._searchFields[fieldValue];
            const searchCheck = (order) => {
                if (!fieldAccessor) return true;
                const fieldValue = fieldAccessor(order);
                if (fieldValue === null) return true;
                if (!searchTerm) return true;
                return fieldValue && fieldValue.toString().toLowerCase().includes(searchTerm.toLowerCase());
            };
            const predicate = (order) => {
                return filterCheck(order) && searchCheck(order);
            };
            return this.Invoices.filter(predicate);
        }
        _closeInvoiceScreen(){
            this.close();
        }
    }
    InvoiceScreen.template = 'InvoiceScreen';

    Registries.Component.add(InvoiceScreen);

    return InvoiceScreen;
});
