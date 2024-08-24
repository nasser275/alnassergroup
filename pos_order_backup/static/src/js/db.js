/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_order_backup.db', function (require) {
    "use strict";
    var pos_db = require("point_of_sale.DB")
    var models = require("point_of_sale.models");
    var SuperPosModel = models.PosModel.prototype;

    models.PosModel = models.PosModel.extend({
        set_synch: function(status, pending) {
            SuperPosModel.set_synch.call(this,status,pending)
            if ((status == 'error') || (status == 'disconnected')){
                $(".order-backup-btn").show()
            }
            else{
                $(".order-backup-btn").hide();  
            }
        },
    });

    pos_db.include({
        clear_cached_orders: function(){
            this.cache.orders = [];
            let required_key = Object.keys(localStorage).find(key =>{
                return key.startsWith("openerp_pos_db") && key.endsWith("orders") && !key.endsWith("unpaid_orders");
            });
            localStorage[required_key] = [];
        },
        download_cached_orders: function(session_name){
            let cached_orders = this.cache.orders;
            let order_data = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(cached_orders));
            let download_element = document.getElementById('json_download_element');
            let json_file_name = session_name + new Date().toLocaleTimeString().toString() + ".json";
            download_element.setAttribute("href", order_data);
            download_element.setAttribute("download", json_file_name);
            download_element.click();
        },
    });
});
