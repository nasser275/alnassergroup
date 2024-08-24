odoo.define('aspl_pos_combo.pos', function (require) {
    "use strict";
    var models = require('point_of_sale.models');
    const {Gui} = require('point_of_sale.Gui');
    var existing_models = models.PosModel.prototype.models;
    var product_index = _.findIndex(existing_models, function (model) {
        return model.model === "product.product";
    });
    var product_model = existing_models[product_index];
    var fields = product_model.fields;
    fields.push('is_combo')
    fields.push('product_combo_ids')
    fields.push('combo_date_start')
    fields.push('combo_date_end')
    fields.push('combo_limit')
    fields.push('combo_cost')
    fields.push('combo_price')
    fields.push('pos_load')
    fields.push('price_w_o_tax')
    fields.push('hide_discount')
    models.load_models([{
        model: product_model.model,
        fields: fields,
        order: product_model.order,
        domain: product_model.domain,
        context: product_model.context,
        loaded: product_model.loaded,
    }]);

    models.load_models({
        model: 'product.combo',
        loaded: function (self, product_combo) {
            self.product_combo = product_combo;
        }
    });

    function check_expiry(start, end) {
        var today = moment().lang('en').format('YYYY-MM-DD');
        if (start && end) {
            if (today < start || today > end)
                return false;
        } else if (start) {
            if (today < start)
                return false;
        } else if (end) {
            if (today > end)
                return false;
        }
        return true;
    }


    var _super_Order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (attr, options) {
            _super_Order.initialize.call(this, attr, options);
        },
        export_as_JSON: function () {
            var json = _super_Order.export_as_JSON.apply(this, arguments);
            return json;
        },
        init_from_JSON: function (json) {
            _super_Order.init_from_JSON.apply(this, arguments);
        },

        add_product: function (product, options) {
            var self = this;
            if (self.pos.config.enable_discount) {
                if (1==0) {

                } else {
                    _super_Order.add_product.call(this, product, options);
                    if (product.is_combo && product.product_combo_ids.length > 0 && self.pos.config.enable_combo) {
                        Gui.showPopup('POSComboProductPopup', {
                            'product': product,
                        });
                    }
                }
            } else {
                _super_Order.add_product.call(this, product, options);
                if (product.is_combo && product.product_combo_ids.length > 0 && self.pos.config.enable_combo) {
                    Gui.showPopup('POSComboProductPopup', {
                        'product': product,
                    });
                }
            }


        },
        build_line_resume: function () {
            var self = this;
            var resume = {};

            this.orderlines.each(function (line) {
                if (line.mp_skip) {
                    return;
                }
                var line_hash = line.get_line_diff_hash();
                var qty = Number(line.get_quantity());
                var note = line.get_note();
                var product_id = line.get_product().id;

                if (typeof resume[line_hash] === 'undefined') {
                    var combo_info = false;
                    if (line.combo_prod_info && line.combo_prod_info.length > 0) {
                        combo_info = line.combo_prod_info;
                    }
                    resume[line_hash] = {
                        qty: qty,
                        note: note,
                        product_id: product_id,
                        product_name_wrapped: line.generate_wrapped_product_name(),
                        combo_info: combo_info || false,
                    };
                } else {
                    resume[line_hash].qty += qty;
                    resume[line_hash].combo_info = combo_info;
                }
            });
            return resume;
        },
        computeChanges: function (categories) {
            var current_res = this.build_line_resume();
            var old_res = this.saved_resume || {};
            var json = this.export_as_JSON();
            var add = [];
            var rem = [];
            var line_hash;

            for (line_hash in current_res) {
                var curr = current_res[line_hash];
                var old = old_res[line_hash];

                if (typeof old === 'undefined') {
                    add.push({
                        'id': curr.product_id,
                        'name': this.pos.db.get_product_by_id(curr.product_id).display_name,
                        'name_wrapped': curr.product_name_wrapped,
                        'note': curr.note,
                        'qty': curr.qty,
                        'combo_info': curr.combo_info,
                    });
                } else if (old.qty < curr.qty) {
                    add.push({
                        'id': curr.product_id,
                        'name': this.pos.db.get_product_by_id(curr.product_id).display_name,
                        'name_wrapped': curr.product_name_wrapped,
                        'note': curr.note,
                        'qty': curr.qty - old.qty,
                        'combo_info': curr.combo_info,
                    });
                } else if (old.qty > curr.qty) {
                    rem.push({
                        'id': curr.product_id,
                        'name': this.pos.db.get_product_by_id(curr.product_id).display_name,
                        'name_wrapped': curr.product_name_wrapped,
                        'note': curr.note,
                        'qty': old.qty - curr.qty,
                        'combo_info': curr.combo_info,
                    });
                }
            }

            for (line_hash in old_res) {
                if (typeof current_res[line_hash] === 'undefined') {
                    var old = old_res[line_hash];
                    if (old) {
                        rem.push({
                            'id': old.product_id,
                            'name': this.pos.db.get_product_by_id(old.product_id).display_name,
                            'name_wrapped': old.product_name_wrapped,
                            'note': old.note,
                            'qty': old.qty,
                            'combo_info': old.combo_info,
                        });
                    }
                }
            }

            if (categories && categories.length > 0) {
                // filter the added and removed orders to only contains
                // products that belong to one of the categories supplied as a parameter

                var self = this;

                var _add = [];
                var _rem = [];

                for (var i = 0; i < add.length; i++) {
                    if (self.pos.db.is_product_in_category(categories, add[i].id)) {
                        _add.push(add[i]);
                    }
                }
                add = _add;

                for (var i = 0; i < rem.length; i++) {
                    if (self.pos.db.is_product_in_category(categories, rem[i].id)) {
                        _rem.push(rem[i]);
                    }
                }
                rem = _rem;
            }

            var d = new Date();
            var hours = '' + d.getHours();
            hours = hours.length < 2 ? ('0' + hours) : hours;
            var minutes = '' + d.getMinutes();
            minutes = minutes.length < 2 ? ('0' + minutes) : minutes;

            return {
                'new': add,
                'cancelled': rem,
                'table': json.table || false,
                'floor': json.floor || false,
                'name': json.name || 'unknown order',
                'time': {
                    'hours': hours,
                    'minutes': minutes,
                },
            };

        },
    });

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function (attr, options) {
            this.combo_prod_info = false;
            this.combo_name = false;
            this.is_combo = false;
            this.main_combo = false;
            // this.combo_cost = 0;
            // this.combo_price = 0;
            _super_orderline.initialize.call(this, attr, options);
        },
        init_from_JSON: function (json) {
            var self = this;
            _super_orderline.init_from_JSON.apply(this, arguments);
            var new_combo_data = [];
            if (json.combo_ext_line_info && json.combo_ext_line_info.length > 0) {
                json.combo_ext_line_info.map(function (combo_data) {
                    if (combo_data[2].product_id) {
                        var product = self.pos.db.get_product_by_id(combo_data[2].product_id);
                        if (product) {
                            new_combo_data.push({
                                'product': product,
                                'price': combo_data[2].price,
                                'qty': combo_data[2].qty,
                                'id': combo_data[2].id,
                            });
                        }
                    }
                });
            }
            this.combo_name = json.combo_name;
            this.is_combo = json.is_combo;
            this.main_combo = json.main_combo;
            self.set_combo_prod_info(new_combo_data);
        },
        set_combo_prod_info: function (combo_prod_info) {
            this.combo_prod_info = combo_prod_info;
            this.trigger('change', this);
        },
        get_combo_prod_info: function () {
            console.log("get_combo_prod_info", this.combo_prod_info)
            return this.combo_prod_info;
        },
        export_as_JSON: function () {
            var self = this;
            var json = _super_orderline.export_as_JSON.call(this, arguments);
            var combo_ext_line_info = [];
            if (this.product.is_combo && this.combo_prod_info.length > 0) {
                _.each(this.combo_prod_info, function (item) {
                var _product=self.pos.db.get_product_by_id(item.product.id)
                console.log(">D>D>",_product)
                    combo_ext_line_info.push([0, 0, {
                        'product_id': item.product.id,
                        'product_name': _product.display_name,
                        'qty': item.qty,
                        'price': item.price,
                        'id': item.id,
                        'combo_id':item.id,
                        'discount': item.discount,
                        'combo_name': item.combo_name,
                        'tax':_product.taxes_id.length>0 ? true : false,
                         'price_w_o_tax':(_product.price_w_o_tax*item.qty)*(1-(item.discount/100))

                    }]);
                });
            }

            json.combo_ext_line_info = this.product.is_combo ? combo_ext_line_info : [];
            console.log("combo_ext_line_info", combo_ext_line_info)
            json.combo_name = this.product.is_combo ? this.product.display_name : "";
            json.combo_cost = this.product.is_combo ? this.combo_cost : 0;
            json.combo_price = this.product.is_combo ? this.combo_price : 0;
            return json;
        },
        can_be_merged_with: function (orderline) {
            var result = _super_orderline.can_be_merged_with.call(this, orderline);
            if (orderline.product.id == this.product.id && this.get_combo_prod_info()) {
                return false;
            }
            return result;
        },
        export_for_printing: function () {
            var lines = _super_orderline.export_for_printing.call(this);
            lines.combo_prod_info = this.get_combo_prod_info();
            lines.main_combo = this.main_combo;
            return lines;
        },
    });


});