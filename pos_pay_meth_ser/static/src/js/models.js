odoo.define('pos_pay_meth_ser.load_data', function (require) {
    "use strict";


    var models = require('point_of_sale.models');





    var _super = models.Order;
    models.Order = models.Order.extend({
        export_as_JSON: function () {
            var json = _super.prototype.export_as_JSON.apply(this, arguments);
            json.payment_serial_no = this.payment_serial_no;

            return json;
        },
        init_from_JSON: function (json) {
            _super.prototype.init_from_JSON.apply(this, arguments);
            this.payment_serial_no = json.payment_serial_no;

        },
    });




});