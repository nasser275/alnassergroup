odoo.define('healthy_app_orders.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var gui = require('point_of_sale.Gui');
    var core = require('web.core');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');
    var _t = require('web.core')._t;
    var session = require('web.session');
    var today_domain = new Date().toISOString().slice(0, 10);
    var ajax = require('web.ajax');
    console.log("today_domain", today_domain)
    // models.load_models({
    //     model: 'app.order',
    //     orderBy: [{name: 'id', asc: -1}],
    //     domain: function (self) {
    //     if (self.config.branch_id){
    //                 var domain = [['state', 'in', ['draft']], ['order_date', '=', today_domain],['branch_id', '=', self.config.branch_id[0]]]
    //     }else{
    //                 var domain = [['state', 'in', ['draft']], ['order_date', '=', today_domain]]
    //     }
    //         console.log("test domain",domain)
    //         return domain;
    //
    //     },
    //         loaded: function (self, orders) {
    //
    //             self.orders = orders;
    //         }
    //     });
    // models.load_models({
    //     model: 'app.order.lines',
    //       domain: function (self) {
    //     if (self.config.branch_id){
    //                 var domain = [['app_order_id.branch_id', '=', self.config.branch_id[0]]]
    //     }else{
    //                 var domain = []
    //     }
    //         console.log("test domain",domain)
    //         return domain;
    //
    //     },
    //         loaded: function (self, order_lines) {
    //             self.order_lines = order_lines;
    //         }
    //     });
    //
    //

    var _super = models.Order;
    models.Order = models.Order.extend({
        export_as_JSON: function () {
            var json = _super.prototype.export_as_JSON.apply(this, arguments);
            json.app_order_id = this.app_order_id;
            return json;
        },
        init_from_JSON: function (json) {
            _super.prototype.init_from_JSON.apply(this, arguments);
            this.app_order_id = json.app_order_id;

        },
    });
    var posmodel_super = models.PosModel.prototype;
    models.PosModel =models.PosModel.extend({
        after_load_server_data: async function () {
            this.sync_app_orders()
            return posmodel_super.after_load_server_data.apply(this, arguments);
        },
        sync_app_orders: function () {
            setInterval(function () {
                 $.ajax({
                url: '/checkapporder',
                type: "GET",
                success: function (data) {console.log(data);
                 if (data=='yes'){
                     alert("App Order Received!")
                 }
                },
                error: function (data) {
                    console.log("error!");
                }
            });
            }, 10000);
        }

    });
});