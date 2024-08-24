odoo.define('phi_pos_loyalty_exclude_customer.pos_loyalty', function (require) {
"use strict";

    var models = require('point_of_sale.models');


    models.load_fields('res.partner','is_loyalty_exclude');

    var _super = models.Order;
    models.Order = models.Order.extend({
        get_won_points: function(){
            if (!this.pos.loyalty || !this.get_client() || this.get_client().is_loyalty_exclude) {
                return 0;
            }
            return _super.prototype.get_won_points.apply(this);
        },
        get_spent_points: function(){
            if (!this.pos.loyalty || !this.get_client() || this.get_client().is_loyalty_exclude) {
                return 0;
            }
            return _super.prototype.get_spent_points.apply(this);
        },

        get_new_points: function(){
            if (!this.pos.loyalty || !this.get_client() || this.get_client().is_loyalty_exclude) {
                return 0;
            }
            return _super.prototype.get_new_points.apply(this);
        },

        get_new_total_points: function(){
            if (!this.pos.loyalty || !this.get_client() || this.get_client().is_loyalty_exclude) {
                return 0;
            }
            return _super.prototype.get_new_total_points.apply(this);
        },

        get_spendable_points: function(){
            if (!this.pos.loyalty || !this.get_client() || this.get_client().is_loyalty_exclude) {
                return 0;
            }
            return _super.prototype.get_spendable_points.apply(this);
        },

        export_for_printing: function(){
            var json = _super.prototype.export_for_printing.apply(this,arguments);
            if (this.pos.loyalty && this.get_client() && this.get_client().is_loyalty_exclude) {
                json.loyalty = false;
            } else {
                if (this.pos.loyalty && this.get_client()) {
                    json.loyalty = {
                        rounding:     this.pos.loyalty.rounding || 1,
                        name:         this.pos.loyalty.name,
                        client:       this.get_client().name,
                        points_actual:this.get_client().loyalty_points,
                        points_won  : this.get_won_points(),
                        points_spent: this.get_spent_points(),
                        points_total: this.get_new_total_points(),
                    };
                }
            }
            return json;
        },

    });


});