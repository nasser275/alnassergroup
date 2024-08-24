odoo.define('healthy_salesperson.load_data_hr', function (require) {
    "use strict";


    var models = require('point_of_sale.models');


    models.load_models({
        model: 'hr.employee',
        domain: [['is_sales_person','=',true]],
        loaded: function (self, salespersons) {
            self.salespersons = salespersons;
        }
    });


    var _super = models.Order;
    models.Order = models.Order.extend({
        export_as_JSON: function () {
            var json = _super.prototype.export_as_JSON.apply(this, arguments);
            json.sales_person = this.sales_person;
            return json;
        },
        init_from_JSON: function (json) {
            _super.prototype.init_from_JSON.apply(this, arguments);
            this.sales_person = json.sales_person;
        },




    });



});