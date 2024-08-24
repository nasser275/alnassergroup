odoo.define('healthy_pos_receipt.rec', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
// New orders are now associated with the current table, if any.

    var _super_order = models.Order.prototype;
    var _super_order_line = models.Orderline.prototype;
    models.Order = models.Order.extend({

        export_for_printing: function () {
            var order = this.pos.get_order();
            var json = _super_order.export_for_printing.apply(this, arguments);
            if (this.pos.pos_session.branch_id) {
                json.branch_name = this.pos.pos_session.branch_id[1];
                json.pos_branch = this.pos.pos_session.pos_branch;
            } else {
                json.branch_name = ""
                json.pos_branch = ""

            }
            json.delivery_amount = this.delivery_amount
            json.person_name = this.get_person_name(this.delivery_person_id)

            console.log("_super_order", json)
            return json;
        },
        get_person_name: function (delivery_person_id) {
            console.log("this.pos.delivery_persons", this.pos.delivery_persons)
            for (var i = 0; i < this.pos.delivery_persons.length; i++) {
                if (this.pos.delivery_persons[i].id == parseInt(delivery_person_id)) {
                    return this.pos.delivery_persons[i].name

                }
            }

        }

    });
    models.Orderline = models.Orderline.extend({

        export_for_printing: function () {
            var json = _super_order_line.export_for_printing.apply(this, arguments);
            json.is_delivery_charge =this.get_product().display_name=="Delivery" ? true : false;
            return json;
        },

    });

});
