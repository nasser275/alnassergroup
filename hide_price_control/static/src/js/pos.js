odoo.define('hide_price_control.hide_price', function (require) {
    "use strict";

    const NumpadWidget = require('point_of_sale.NumpadWidget');
    const Registries = require('point_of_sale.Registries');

    var models = require('point_of_sale.models');

    models.load_models(
        {
            model: 'res.users',
            fields: ['name', 'company_id', 'id', 'groups_id', 'lang', 'show_price_control','use_pos_password','user_password','show_discount_control','can_edit_open_cash_control','show_cash_in_out'],
            domain: function (self) {
                return [['company_ids', 'in', self.config.company_id[0]], '|', ['groups_id', '=', self.config.group_pos_manager_id[0]], ['groups_id', '=', self.config.group_pos_user_id[0]]];
            },
            loaded: function (self, users) {
                users.forEach(function (user) {
                    user.role = 'cashier';
                    user.groups_id.some(function (group_id) {
                        if (group_id === self.config.group_pos_manager_id[0]) {
                            user.role = 'manager';
                            return true;
                        }
                    });
                    if (user.id === self.session.uid) {
                        console.log(">F",user)
                        self.user = user;
                        self.employee.name = user.name;
                        self.employee.role = user.role;
                        self.employee.user_id = [user.id, user.name];
                        self.employee.show_price_control = user.show_price_control;
                        self.employee.show_discount_control = user.show_discount_control;
                        self.employee.use_pos_password = user.use_pos_password;
                        self.employee.user_password = user.user_password;
                        self.employee.show_cash_in_out = user.show_cash_in_out;
                    }
                });
                self.users = users;
                self.employees = [self.employee];
                self.set_cashier(self.employee);
            },
        }
    );

    const CNumpadWidget = NumpadWidget =>
        class extends NumpadWidget {
            get hasPriceControlRights() {
                const cashier = this.env.pos.get('cashier') || this.env.pos.get_cashier();
                return cashier.show_price_control;
            }
            get hasManualDiscount() {
                const cashier = this.env.pos.get('cashier') || this.env.pos.get_cashier();
            // return this.env.pos.config.manual_discount && !this.props.disabledModes.includes('discount');
            return cashier.show_discount_control;
        }


        };

    Registries.Component.extend(NumpadWidget, CNumpadWidget);

    return NumpadWidget;


});
