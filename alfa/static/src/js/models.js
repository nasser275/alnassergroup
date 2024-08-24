odoo.define('aspl_pos_create_so_extension.models', function (require) {
"use strict";

    var models = require('point_of_sale.models');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var _t = core._t;
    var utils = require('web.utils');
    var round_pr = utils.round_precision;

    models.load_fields("res.users", ['display_own_sales_order','sale_order_operations','sale_order_invoice']);

    var _super_Order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attr, options){
            _super_Order.initialize.call(this,attr,options);
            this.sign = this.sign || null;
            this.raw_sign = this.raw_sign || null;
            this.order_note = this.order_note || null;
            this.sale_order_mode = true;
            this.shipping_address = this.shipping_address || null;
            this.invoice_address = this.invoice_address || null;
            this.is_quotation = false;
            this.sale_order_id = this.sale_order_id || null;
            this.sale_order_id_to_edit = this.sale_order_id_to_edit || null;
            this.sale_order_pay = false;
            this.invoice_id = this.invoice_id || null;
        },
        init_from_JSON: function(json){
            _super_Order.init_from_JSON.apply(this,arguments);
            this.sign = json.sign;
            this.raw_sign = json.raw_sign;
            this.sale_order_mode = json.sale_order_mode;
        },
        set_order_note : function(order_note){
            this.order_note = order_note;
        },
        get_order_note : function(order_note){
            return this.order_note;
        },
        set_sale_order_mode: function(sale_order_mode){
            this.sale_order_mode = sale_order_mode;
             this.trigger('change',this);
        },
        get_sale_order_mode: function(sale_order_mode){
            return this.sale_order_mode;
        },
        set_sign: function(sign){
            this.sign = sign;
            this.trigger('change',this);
        },
        get_sign: function(){
            return this.sign;
        },
        set_raw_sign : function(sign){
            this.raw_sign = sign;
            this.trigger('change',this);
        },
        get_raw_sign : function(){
            return this.raw_sign;
        },
        set_shipping_address: function(val){
            this.shipping_address = val;
        },
        get_shipping_address: function(){
            return this.shipping_address;
        },
        set_invoice_address: function(val){
            this.invoice_address = val;
        },
        get_invoice_address: function(){
            return this.invoice_address;
        },
        set_is_quotation: function(val){
            this.is_quotation = val;
        },
        get_is_quotation: function(){
            return this.is_quotation;
        },
        set_sale_order_id: function(val){
            this.sale_order_id = val;
        },
        get_sale_order_id: function(){
            return this.sale_order_id;
        },
        set_sale_order_id_to_edit: function(val){
            this.sale_order_id_to_edit = val;
        },
        get_sale_order_id_to_edit: function(){
            return this.sale_order_id_to_edit;
        },
        set_sale_order_pay: function(val){
            this.sale_order_pay = val;
        },
        get_sale_order_pay: function(){
            return this.sale_order_pay;
        },
        set_invoice_id:function(invoice_id){
            this.invoice_id = invoice_id;
        },
        get_invoice_id: function(){
            return this.invoice_id;
        },
        export_as_JSON: function(){
            var orders = _super_Order.export_as_JSON.call(this);
            orders.sign = this.sign || false;
            orders.raw_sign = this.raw_sign || false;
            orders.sale_order_mode = this.sale_order_mode || false;
            return orders;
        },
    });

    var _posModelSuper = models.PosModel;
    models.PosModel = models.PosModel.extend({
        load_server_data: function(){
            var self = this;
            var loaded = _posModelSuper.prototype.load_server_data.call(this);
            loaded.then(function(){
                 var params = {
                    model: 'sale.order',
                    method: 'get_sale_order_data',
                    args:[self.user]
                 }
                 self.rpc(params).then(function(res){
                    self.env.pos.db.add_orders(res[0]);
                    self.env.pos.db.add_invoices(res[1]);
                 });
            })
            return loaded
        },
    });
});


