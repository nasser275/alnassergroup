odoo.define('aspl_pos_create_so_extension.db', function (require) {
    "use strict";

    var DB = require('point_of_sale.DB');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var _t = core._t;

    DB.include({
        init: function(options){
            this._super.apply(this, arguments);
            this.orders_list = [];
            this.invoices_list = [];
            this.orders_list_by_id = {};
            this.invoices_list_by_id = {};
        },
        add_orders : function(orders){
            this.orders_list = orders
            for(var i = 0; i < orders.length; i++){
                var order = orders[i];
                let localTime =  moment.utc(order['date_order']).toDate();
                order['date_order'] =  moment(localTime).format('YYYY-MM-DD hh:mm:ss')
                if (!this.orders_list_by_id[order.id]){
                   this.orders_list_by_id[order.id] = order;
                }
            }
        },
        add_invoices : function(invoices){
            this.invoices_list = invoices;
            for(var i = 0; i < invoices.length; i++){
                var invoice = invoices[i];
                let localTime =  moment.utc(invoice['date_order']).toDate();
                invoice['date_order'] =  moment(localTime).format('YYYY-MM-DD hh:mm:ss')
                if (!this.invoices_list_by_id[invoice.id]){
                   this.invoices_list_by_id[invoice.id] = invoice;
                }
            }
        },
        get_order_by_id: function(id){
            return this.orders_list_by_id[id];
        },
        get_invoice_by_id: function(id){
            return this.orders_list_by_id[id];
        },
        get_orders_list: function(){
            return this.orders_list;
        },
        get_invoices_list: function(){
            return this.invoices_list;
        },
    });
});