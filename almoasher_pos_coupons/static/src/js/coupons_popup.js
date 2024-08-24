odoo.define('almoasher_pos_coupons.coupons_popup', function (require) {
        "use strict";

        const Registries = require('point_of_sale.Registries');
        const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
        var core = require('web.core');
        var pos_model = require('point_of_sale.models');
        var pos_model = require('point_of_sale.models');
        var models = pos_model.PosModel.prototype.models;
        var field_utils = require('web.field_utils');
        var OrderSuper = pos_model.Order;
        var core = require('web.core');
        var _t = core._t;
        var utils = require('web.utils');
        var round_pr = utils.round_precision;
        const {
            useState,
            useRef
        } = owl.hooks;


        // getting vouchers and coupons
        models.push({
            model: 'pos.coupon',
            fields: [],
            // domain: function(self) {
            //     return [['state', 'not in', ['unactive']]];
            // },
            loaded: function (self, coupons) {
                // self.db.all_coupons = coupons;
                self.db.coupons_by_code = {};
                self.db.coupons_by_id = {};
                coupons.forEach(function (coupon) {
                    if (coupon.state == 'active') {
                        var coupon_data = {
                            'coupon_id': coupon.id,
                            'state': 'available'
                        }
                        self.update_pos_coupon_data_to_backend(coupon_data)
                    }
                    self.db.coupons_by_code[coupon.name] = coupon;
                    self.db.coupons_by_id[coupon.id] = coupon;
                });
            },
        },);


        pos_model.PosModel = pos_model.PosModel.extend({
            get_data_from_backend_coupons: function () {
                var self = this;
                var status = new $.Deferred();
                var args = [
                    []
                ];
                self.rpc({
                    model: 'pos.coupon',
                    method: 'sync_pos_coupon_to_pos',
                    args: args
                }).then(function (results) {
                    if (results['not_synced_read'] && results['not_synced_read'].length) {
                        results['not_synced_read'].forEach(function (data) {
                            // self.db.all_coupons.push(data);
                            self.db.coupons_by_code[data['name']] = data;
                            self.db.coupons_by_id[data['id']] = data;
                        });
                        status.resolve();
                    }
                    // if (results['not_synced_lines_read'] && results['not_synced_lines_read'].length) {
                    //     results['not_synced_lines_read'].forEach(function (data) {
                    //         // self.db.all_coupons_line.push(data)
                    //         // self.db.coupons_line_by_coupon_code[data.coupon_id[1]] = data;
                    //         self.db.coupons_line_by_coupon_id[line.coupon_id[0]] = data;
                    //         if(line.state == 'confirmed'){
                    //             self.db.confirmed_coupons_line_by_order_name[data.order_name] = data;
                    //         }else if(line.state == 'done'){
                    //             self.db.done_coupons_line_by_order_name[data.order_name] = data;
                    //         }
                    //     });
                    //     status.resolve();
                    // }
                });
                return status;
            },
            delete_by_id: function (data, id) {
                if (data && id) {
                    data.splice(_.indexOf(data, _.findWhere(data, {
                        id: id
                    })), 1);
                } else {
                    return this.showPopup('ErrorPopup', {title: "Error", body: "error while delete coupon"});
                }
            },
            update_pos_coupon_data_to_backend: function (data) {
                var self = this;
                var status = new $.Deferred();
                self.rpc({
                    model: 'pos.coupon',
                    method: 'action_update_data_from_pos',
                    args: [data]
                }).then(function (data) {
                    //// console.log(data);
                    if (data && data['id']) {
                        var coupon = self.db.coupons_by_id[data['id']]
                        if (coupon) {
                            //// console.log('coupon before update', coupon);
                            coupon.state = data['state'];
                            coupon.used_times = data['used_times'];
                            coupon.partner_total = data['partner_total'];
                            //// console.log('coupon after update', coupon);
                        }
                    }
                    status.resolve();
                    // self.pos.db.all_app_orders.splice(_.indexOf(self.pos.db.all_app_orders, _.findWhere(self.pos.db.all_app_orders, { id : result})), 1);
                });
                return status;
            },
            get_last_confirmed_coupon_line_by_order: function (order_name, coupon_id = false) {
                var self = this;
                var status = new $.Deferred();
                var order = self.get_order();
                self.rpc({
                    model: 'pos.coupon',
                    method: 'get_last_confirmed_coupon_line_by_order',
                    args: [order_name, coupon_id]
                }).then(function (data) {
                    // console.log("get_last_confirmed_coupon_line_by_order", data);
                    if (data.length) {
                        var coupon = self.db.coupons_by_id[data[id]]
                        if (coupon) {
                            order.coupon = coupon
                        } else {
                            order.coupon = false
                        }
                    } else {
                        order.coupon = false
                    }
                    status.resolve();
                    // self.pos.db.all_app_orders.splice(_.indexOf(self.pos.db.all_app_orders, _.findWhere(self.pos.db.all_app_orders, { id : result})), 1);
                });
                return status;
            },
            get_deleted_data_from_backend_pos_coupon: function () {
                var self = this;
                var status = new $.Deferred();
                var args = [
                    []
                ];
                self.rpc({
                    model: 'pos.coupon',
                    method: 'sync_deleted_pos_coupon_to_pos',
                    args: args
                }).then(function (results) {
                    if (results['deleted_not_synced_read'] && results['deleted_not_synced_read'].length) {
                        results['deleted_not_synced_read'].forEach(function (id) {
                            //// console.log('id', id);
                            var deleted_order_by_id = self.db.coupons_by_id[id];
                            var deleted_order_by_code = self.db.coupons_by_code[deleted_order_by_id['name']];
                            //// console.log('deleted_order_by_id, deleted_order_by_code', deleted_order_by_id, deleted_order_by_code);
                            if (deleted_order_by_id !== undefined) {
                                deleted_order_by_id['state'] = 'deleted'
                                // self.delete_by_id(self.db.coupons_by_id, id);
                            }
                            if (deleted_order_by_code !== undefined) {
                                deleted_order_by_code['state'] = 'deleted'
                                // self.delete_by_id(self.db.coupons_by_id, id);
                            }
                        });
                        status.resolve();
                    }
                    // if (results['deleted_synced_lines_read'] && results['deleted_synced_lines_read'].length) {
                    //     results['deleted_synced_lines_read'].forEach(function (id) {
                    //         //// console.log('id', id);
                    //         line_id = self.db.coupons_line_by_coupon_id[id]
                    //         if(line.state == 'confirmed'){
                    //             delete self.db.confirmed_coupons_line_by_order_name[line_id.order_name]
                    //         }else if(line.state == 'done'){
                    //             delete self.db.done_coupons_line_by_order_name[line_id.order_name]
                    //         }
                    //         delete self.db.coupons_line_by_coupon_id[id]
                    //     });
                    //     status.resolve();
                    // }
                });
                return status;
            },
            refresh_coupons_data: function () {
                this.get_data_from_backend_coupons();
                this.get_deleted_data_from_backend_pos_coupon();
            },
        });
        pos_model.Orderline = pos_model.Orderline.extend({
            // set_quantity: function(quantity, keep_price){
            //     // console.log("#####################################")
            //     var self = this;
            //     var order = self.order
            //     var quant = parseFloat(quantity) || 0;
            //     var product = this.get_product();
            //     console.log("QUANTITY ==================",order.coupon, order);
            //     order.do_coupon_operation()
            //     // if(order.do_coupon_operation()){
            //     // return PosModelOrderline.prototype.set_quantity.call(this, quantity, keep_price);
            //     // }
            //     return PosModelOrderline.prototype.set_quantity.call(this, quantity, keep_price);
            // },
             set_quantity: function(quantity, keep_price){
        this.order.assert_editable();
        if(quantity === 'remove'){
            if (this.refunded_orderline_id in this.pos.toRefundLines) {
                delete this.pos.toRefundLines[this.refunded_orderline_id];
            }
            this.order.remove_orderline(this);
            this.order.do_coupon_operation()
            return true;
        }
        else{
            var quant = typeof(quantity) === 'number' ? quantity : (field_utils.parse.float('' + quantity) || 0);
            if (this.refunded_orderline_id in this.pos.toRefundLines) {
                const toRefundDetail = this.pos.toRefundLines[this.refunded_orderline_id];
                const maxQtyToRefund = toRefundDetail.orderline.qty - toRefundDetail.orderline.refundedQty
                if (quant > 0) {
                    Gui.showPopup('ErrorPopup', {
                        title: _t('Positive quantity not allowed'),
                        body: _t('Only a negative quantity is allowed for this refund line. Click on +/- to modify the quantity to be refunded.')
                    });
                    return false;
                } else if (quant == 0) {
                    toRefundDetail.qty = 0;
                } else if (-quant <= maxQtyToRefund) {
                    toRefundDetail.qty = -quant;
                } else {
                    Gui.showPopup('ErrorPopup', {
                        title: _t('Greater than allowed'),
                        body: _.str.sprintf(
                            _t('The requested quantity to be refunded is higher than the refundable quantity of %s.'),
                            this.pos.formatProductQty(maxQtyToRefund)
                        ),
                    });
                    return false;
                }
            }
            var unit = this.get_unit();
              if (this.product.display_name === "POS-Coupon-Product" && this.quantity > 0) {
                        console.log("QUANTITY this product ==================", self);
                        return;
                    }
                    else{
                       if(unit){
                if (unit.rounding) {
                    var decimals = this.pos.dp['Product Unit of Measure'];
                    var rounding = Math.max(unit.rounding, Math.pow(10, -decimals));
                    this.quantity    = round_pr(quant, rounding);
                    this.quantityStr = field_utils.format.float(this.quantity, {digits: [69, decimals]});
                } else {
                    this.quantity    = round_pr(quant, 1);
                    this.quantityStr = this.quantity.toFixed(0);
                }
            }else{
                this.quantity    = quant;
                this.quantityStr = '' + this.quantity;
            }

                    }

        }

        // just like in sale.order changing the quantity will recompute the unit price
        if (!keep_price && !this.price_manually_set && !(
            this.pos.config.product_configurator && _.some(this.product.attribute_line_ids, (id) => id in this.pos.attributes_by_ptal_id))){
            this.set_unit_price(this.product.get_price(this.order.pricelist, this.get_quantity(), this.get_price_extra()));
            this.order.fix_tax_included_price(this);
        }
        this.trigger('change', this);
        return true;
    },
        });
        pos_model.Order = pos_model.Order.extend({
            initialize: function (attributes, options) {
                // this.order_coupon_ids = [];
                // this.partner_coupon_ids = {};
                this.coupon = false;
                return OrderSuper.prototype.initialize.call(this, attributes, options);
                ;
            },
            // add_product: function(product, options){
            //     options = options || {};
            //     var self=this;
            //     console.log(" ADD ==================",self.coupon);
            //     if(self.do_coupon_operation()){
            //         return OrderSuper.prototype.add_product.call(this, product, options);
            //     }
            // },
            remove_promotion: function () {
                console.log(">D>>D");
                var self = this;
                var lines = self.orderlines.models
                lines.forEach(function (line) {
                    console.log(">F>F",line,line.promotion)
                    line.set_promotion(false);
                    line.set_rule(false, 0);
                    line.is_promotion=false;
                    line.discount=0;
                });

            },
//            remove_combo: function () {
//                console.log(">D>>D");
//                var self = this;
//                var lines = self.orderlines.models
//                lines.forEach(function (line) {
//                    console.log(">F>F",line)
//                    if (line.is_combo){
//                        self.showPopup('ErrorPopup', {
//                                                    title: self.env._t('Remove Combo'),
//                                                    body: self.env._t(" يجب حذف العرض اولا "),
//
//                                                });
//                    }
//
//                });
//
//            },
            do_coupon_operation: function () {
                var self = this;
                var lines = self.orderlines.models
                if (self.coupon) {
                    if (self.coupon.remove_promotion){
                        self.remove_promotion();
                    }
//                    if (self.coupon.disable_combo){
//                        self.remove_combo();
//                        return false
//                    }
                    self.pos.refresh_coupons_data()
                    var validate = self.check_validity(self.coupon.name)
                    if (validate.coupon_res) {
                        var coupon_data = {
                            'coupon_id': validate.coupon_res.id
                        }
                        self.pos.update_pos_coupon_data_to_backend(coupon_data)
                        console.log("validate", validate);
                        self.handle_remove_products()
                        return true
                    } else {
                        self.coupon = false
                        lines.forEach(function (line) {
                            if (line.product.display_name === "POS-Coupon-Product") {
                                self.orderlines.remove(line);
                                self.coupon = false
                            }
                        })
                        // self.pos.gui.show_popup('coupon-confirm',{
                        //     'title': _t('Unable to apply Coupon !'),
                        //     'body': _t(validate.message +" \n" + "Are you want to remove this order coupon? "),
                        //     confirm: function(){
                        //         self.coupon = false
                        //         self.gui.close_popup();
                        //     },
                        // });
                        return false
                    }
                }
                return false
            },
            remove_orderline: function (line) {
                this.assert_editable();
                var self = this;
                var order = self.pos.get_order()
                // console.log(line, order);
                if (line.product.display_name === "POS-Coupon-Product") {
                    self.coupon = false
                }
                this.orderlines.remove(line);
                this.select_orderline(this.get_last_orderline());
                // self.handle_remove_products()
            },
            handle_remove_products: function () {
                var self = this;
                var lines = self.orderlines.models
                var coupon_product = self.coupon_product ? self.coupon_product : get_coupon_product(self.pos.db.product_by_id);
                var coupon_product = self.pos.db.get_product_by_id(coupon_product);
                if (self.coupon) {
                    var discount_val = self.get_coupon_total_discount(self.coupon);
                    console.log("-------------------", discount_val);
                    if (typeof discount_val !== 'object') {
                        if (!discount_val.status) {
                            if (discount_val) {
                                lines.forEach(function (line) {
                                    if (line.product.display_name === "POS-Coupon-Product") {
                                        console.log("handle remove line, 1", line, discount_val);
                                        line.set_unit_price(discount_val)
                                    }
                                })
                                var line_coupon_product = lines.filter(line => line.product.display_name === "POS-Coupon-Product")
                                if (!line_coupon_product.length) {
                                    console.log("handle remove line, 2", coupon_product, discount_val);
                                    self.add_product(coupon_product, {
                                        quantity: 1,
                                        price: discount_val
                                    });
                                }
                            } else {
                                console.log("self.orderlines.remove(coupon_product) 1", coupon_product, self.orderlines.remove(coupon_product));
                                lines.forEach(function (line) {
                                    if (line.product.display_name === "POS-Coupon-Product") {
                                        self.orderlines.remove(line);
                                        self.coupon = false
                                    }
                                })
                            }
                        } else {
                            console.log("handle remove line, 4", coupon_product, discount_val);
                            self.coupon = false
                            self.orderlines.remove(line);
                        }
                    } else {
                        console.log("self.orderlines.remove(coupon_product) 1", coupon_product, self.orderlines.remove(coupon_product));
                        lines.forEach(function (line) {
                            if (line.product.display_name === "POS-Coupon-Product") {
                                self.orderlines.remove(line);
                                self.coupon = false
                            }
                        })
                    }
                } else {
                    console.log("self.orderlines.remove(coupon_product) 2", coupon_product, self.orderlines.remove(coupon_product));
                    lines.forEach(function (line) {
                        if (line.product.display_name === "POS-Coupon-Product") {
                            self.orderlines.remove(line);
                            self.coupon = false
                        }
                    })
                }
            },
            find_coupon: function (code) {
                console.log(">>", this)
                var coupon = this.pos.db.coupons_by_code[code]
                // console.log("find_coupon", coupon);

                if (coupon) {
                    if (coupon['state'] == 'deleted') {
                        return {
                            'status': false,
                            'message': "This coupon has been deleted."
                        }
                    } else if (coupon['state'] == 'used' && coupon['coupon_usage'] == 'limited') {
                        console.log("DLLLLLLLLLLLLLLLLLLLLLLL", coupon)
                        return {
                            'status': false,
                            'message': "Limit of this coupon is finshed"
                        }
                    } else {
                        return coupon
                    }
                } else {
                    return {
                        'status': false,
                        'message': "This coupon doesn't exist."
                    }
                }
            },
            check_validity: function (coupon_code) {
                // checking it is already used or not
                var self = this;
                var order = this;
                var coupon = self.find_coupon(coupon_code);
                // console.log("coupon data", coupon);
                if (!coupon.status) {
                    // if (coupon){
                    // console.log("typeof coupon !== 'object' && coupon", coupon);
                    var min_order_value = coupon['min_order_value']
                    var coupon_usage = coupon['coupon_usage']
                    var coupon_usage_limit = coupon['coupon_usage_limit']
                    var used_times = coupon['used_times']
                    var combo_dis = coupon['disable_combo']
                    var partner_id = coupon['partner_id']
                    var partner_total = coupon['partner_total']
                    var partner_limit = coupon['partner_limit']
                    console.log('coupon ', coupon);
                    console.log('coupon Discount', coupon['disable_combo']);
                    min_order_value = min_order_value != undefined || min_order_value != null ? min_order_value : 0
                    // if(coupon && !coupon['status']){
                    //// console.log("order.coupon ===============> ", order.coupon);
                    // if(order.coupon && order.coupon == coupon.id){
                    if(partner_id){
                    if (order.get_client().id!==partner_id[0]){
                     return {
                            'status': false,
                            'message': "This coupon Not Available For this Partner"
                        }
                    }else{
                    var discount_val = self.get_coupon_total_discount(coupon);
                    if(partner_total+Math.abs(discount_val)>=partner_limit){
                     return {
                            'status': false,
                            'message': "This coupon Limited "+partner_limit+ " For This Partner "+partner_total
                        }
                    }
                    }
                    }


                    if (combo_dis){
                        var lines = self.orderlines.models
                        var flag = 0
                        lines.forEach(function (line) {
                            console.log(">F>F>F>F11",line)
                            console.log(" Combo Length >F>F>F>F11",line.combo_prod_info.length)
                            if (line.combo_prod_info.length > 0){
                                 console.log(" Length More Than 0",line.combo_prod_info.length)
                                 flag = flag + 1;

                            }

                    });
                    if (flag > 0){
                        console.log(" Combo Flag1",flag)
                        return {
                                                'status': false,
                                                'message': "Sorry Remove Combo First"
                                            }

                    }


                    }

                    if (order.get_total_order2(order.orderlines) >= min_order_value) {
                        if (coupon_usage) {
                            if (coupon_usage == 'limited') {
                                // limited times
                                if (coupon_usage_limit > 0) {
                                    if (used_times >= coupon_usage_limit) {
                                        return {
                                            'status': false,
                                            'message': "Sorry but this coupon is fully used."
                                        }
                                    } else {
                                        return {
                                            'status': true,
                                            'coupon_res': coupon
                                        }
                                    }
                                } else {
                                    return {
                                        'status': false,
                                        'message': "Sorry but this coupon limit < 1."
                                    }
                                }
                            } else {
                                // unlimited
                                return {
                                    'status': true,
                                    'coupon_res': coupon
                                }
                            }
                        } else {

                            return {
                                'status': false,
                                'message': coupon['message']
                            }
                        }

                    } else {
                        return {
                            'status': false,
                            'message': "This coupon used for orders with total " + min_order_value + " or higher."
                        }
                    }
                    // }else{return {'status':false, 'message': "This order already has used coupon before you can not use another one."}}
                    // }else{
                    //     return {'status':false, 'message': coupon['message']}
                    // }
                } else {
                    return {
                        'status': false,
                        'message': coupon['message']
                    }
                }
            },
            get_coupon_total_discount: function (coupon) {
                var self = this;
                var price = -1;
                var order = this;
                var orderlines_model = this.orderlines.models
                var msg = ''
                var total_discount = 0
                var total_price = 0
                var except_check = coupon.except_check;
                var except_product_ids = coupon.except_product_ids;
                var except_category_ids = coupon.except_category_ids;
                var order_total = this.get_total_order(orderlines_model, except_check, except_product_ids, except_category_ids);
                console.log("L<<<<", except_category_ids)
                var total_discount_value = coupon.discount_type == 'fixed' ? coupon.discount_value : order_total * coupon.discount_value / 100
                if (!coupon.status) {
                    if (coupon.calc_by === 'product') {
                        if (coupon.voucher_type === 'product' || coupon.voucher_type === 'multi') {
                            // var result_of_filter = orderlines_model.filter(line => line.product.id == line.product.id)
                            orderlines_model.forEach(function (line) {
                                var product_id = coupon.product_id
                                var discount_value = coupon.discount_type == 'fixed' ? coupon.discount_value : line.price* coupon.discount_value / 100
                                if (coupon.voucher_type == 'multi') {
                                    if (coupon.discount_rule == 'alert') {
                                        var result_of_filter = coupon.product_ids.filter(id => id == line.product.id)
                                        // console.log("result_of_filter", result_of_filter, discount_value);
                                        if (result_of_filter.length) {
                                            if (Math.abs(line.price) >= Math.abs(discount_value)) {
                                                // total_price += line.price
                                                total_discount += discount_value
                                            } else {
                                                console.log("dics value bigger line.product.id , product", line.product.id, line.product.display_name, line.product.display_name);
                                                msg += "Discount value bigger than product price in item [" + line.product.display_name + "] you can allow this option from coupon.\n"
                                                // return;
                                            }
                                        }
                                    } else {
                                        // console.log("!alert line.product.id , product", coupon.product_ids.includes(line.product.id));
                                        if (coupon.product_ids.includes(line.product.id)) {
                                            // total_price += line.price
                                            total_discount += discount_value
                                        }
                                    }
                                } else {
                                    if (coupon.discount_rule == 'alert') {
                                        console.log(" discount_value", line.price, discount_value);
                                        if (Math.abs(line.price) >= Math.abs(discount_value)) {

                                            // console.log("else product line.product.id , product", line.product.id , product);
                                            if (line.product.id == product_id[0]) {
                                                // total_price += line.price
                                                total_discount += discount_value
                                            }
                                        } else {
                                            // console.log("dics value bigger line.product.id , product", line.product.id , product);
                                            msg += "Discount value bigger than product price in item [" + line.product.display_name + "] you can allow this option from coupon.\n"
                                        }
                                    } else {
                                        if (line.product.id == product_id[0]) {
                                            // total_price += line.price
                                            total_discount += discount_value
                                        }
                                    }
                                }
                            })
                        } else {
                            // console.log("type all line.product.id")
                            if (coupon.discount_rule == 'alert') {
                                if (order_total < coupon['discount_value']) {
                                    msg += "Discount value must be less than total order.\n"
                                } else {
                                    var except_check = coupon.except_check;
                                    var except_product_ids = coupon.except_product_ids;
                                    orderlines_model.forEach(function (line) {
                                        if (except_check == 'product') {
                                            if (except_product_ids.includes(line.product.id)) {
                                            } else {
                                                if (line.product.display_name != "POS-Coupon-Product") {
                                                    var discount_value = coupon.discount_type == 'fixed' ? coupon.discount_value : line.price * coupon.discount_value / 100
                                                    total_discount += discount_value
                                                }

                                            }

                                        } else if (except_check == 'category') {
                                            if (except_category_ids.includes(line.product.categ_id[0])) {
                                            } else {
                                                if (line.product.display_name != "POS-Coupon-Product") {
                                                    var discount_value = coupon.discount_type == 'fixed' ? coupon.discount_value : line.price * coupon.discount_value / 100
                                                    total_discount += discount_value
                                                }

                                            }

                                        } else {
                                            if (line.product.display_name != "POS-Coupon-Product") {
                                                var discount_value = coupon.discount_type == 'fixed' ? coupon.discount_value : line.price * coupon.discount_value / 100
                                                total_discount += discount_value
                                            }
                                        }


                                    });
                                    // total_discount = total_discount_value
                                }
                            } else {
                                orderlines_model.forEach(function (line) {
                                    if (except_check == 'product') {
                                        if (except_product_ids.includes(line.product.id)) {
                                        } else {
                                            if (line.product.display_name != "POS-Coupon-Product") {
                                                var discount_value = coupon.discount_type == 'fixed' ? coupon.discount_value : line.price * coupon.discount_value / 100
                                                total_discount += discount_value
                                            }

                                        }

                                    } else if (except_check == 'category') {
                                        if (except_category_ids.includes(line.product.categ_id[0])) {
                                        } else {
                                            if (line.product.display_name != "POS-Coupon-Product") {
                                                var discount_value = coupon.discount_type == 'fixed' ? coupon.discount_value : line.price * coupon.discount_value / 100
                                                total_discount += discount_value
                                            }

                                        }

                                    } else {
                                        if (line.product.display_name != "POS-Coupon-Product") {
                                            var discount_value = coupon.discount_type == 'fixed' ? coupon.discount_value : line.price * coupon.discount_value / 100
                                            total_discount += discount_value
                                        }
                                    }


                                });
                            }
                        }
                    } else {
                        // console.log("calc by total line.product.id , product");
                        if (coupon.discount_rule == 'alert') {
                            // console.log("calc by total line.product.id , 1");
                            if (order_total < coupon.discount_value) {
                                // console.log("calc by total line.product.id , 2");
                                msg += "Discount value must be less than total order.\n"
                            } else {
                                if (coupon.product == 'product') {
                                    var flag = false;
                                    orderlines_model.forEach(function (line) {
                                        if (line.product.display_name != "POS-Coupon-Product" && coupon.product_id[0] == line.product.id) {
                                            flag = true
                                        }

                                    });

                                    // console.log("calc by total line.product.id , 3");
                                    if (flag) {
                                        total_discount = total_discount_value
                                    } else {
                                        total_discount = 0
                                    }


                                } else if (coupon.voucher_type == 'multi') {
                                    var flag = false;
                                    orderlines_model.forEach(function (line) {
                                        if (line.product.display_name != "POS-Coupon-Product" && coupon.product_ids.includes(line.product.id)) {
                                            flag = true
                                        }

                                    });
                                    // console.log("calc by total line.product.id , 3");
                                    if (flag) {
                                        total_discount = total_discount_value
                                    } else {
                                        total_discount = 0
                                    }

                                } else {

                                    // console.log("calc by total line.product.id , 3");
                                    total_discount = total_discount_value
                                }


                            }
                        } else {
                            if (coupon.product == 'product') {
                                var flag = false;
                                orderlines_model.forEach(function (line) {
                                    if (line.product.display_name != "POS-Coupon-Product" && coupon.product_id[0] == line.product.id) {
                                        flag = true
                                    }

                                });

                                // console.log("calc by total line.product.id , 3");
                                if (flag) {
                                    total_discount = total_discount_value
                                } else {
                                    total_discount = 0
                                }


                            } else if (coupon.voucher_type == 'multi') {
                                var flag = false;
                                orderlines_model.forEach(function (line) {
                                    if (line.product.display_name != "POS-Coupon-Product" && coupon.product_ids.includes(line.product.id)) {
                                        flag = true
                                    }

                                });
                                // console.log("calc by total line.product.id , 3");
                                if (flag) {
                                    total_discount = total_discount_value
                                } else {
                                    total_discount = 0
                                }

                            } else {

                                // console.log("calc by total line.product.id , 3");
                                total_discount = total_discount_value
                            }
                        }

                    }
                    console.log("total_discount", total_discount)
                    if (!msg) {
                        // console.log("if(total_discount > 0){", total_discount, coupon.discount_type, coupon);
                        if (total_discount > 0) {
                            price *= total_discount;
                            // console.log("total_discount", total_discount);
                            return price
                        } else {
                            return {
                                'status': false,
                                'message': "sorry but it looks like you dont has any products belong to this coupon."
                            }
                        }
                    } else {
                        // console.log("return {'message': msg}");
                        return {
                            'status': false,
                            'message': msg
                        }
                    }
                } else {
                    // console.log("return {'message': coupon['message']}");
                    return {
                        'status': false,
                        'message': coupon['message']
                    }
                }
            },
            coupon_applied: function (partner_id, coupon) {
                this.coupon = coupon ? coupon : false;
                // this.order_coupon_ids.push(coupon.id);
                // if(partner_id in this.partner_coupon_ids){
                //     this.partner_coupon_ids[partner_id].push(coupon.id);
                // }else{
                //     this.partner_coupon_ids[partner_id] = [coupon.id];
                // }
                this.export_as_JSON();
                return;
            },
            export_as_JSON: function () {
                // var json = _super.prototype.export_as_JSON.apply(this,arguments);
                var self = OrderSuper.prototype.export_as_JSON.call(this);
                self.coupon = this.coupon;
                // self.order_coupon_ids = this.order_coupon_ids;
                // self.partner_coupon_ids = this.partner_coupon_ids
                return self;
            },
            init_from_JSON: function (json) {
                this.coupon = json.coupon;
                // this.order_coupon_ids = json.order_coupon_ids;
                // this.partner_coupon_ids = json.partner_coupon_ids
                OrderSuper.prototype.init_from_JSON.call(this, json);
            },
            // get_total_without_tax: function () {
            //     var res = OrderSuper.prototype.get_total_without_tax.call(this);
            //     var final_res = round_pr(this.orderlines.reduce((function (sum, orderLine) {
            //         return sum + (orderLine.get_unit_price() * orderLine.get_quantity() * (1.0 - (orderLine.get_discount() / 100.0)));
            //     }), 0), this.pos.currency.rounding);
            //     return final_res;
            // },
            get_total_order: function (orderlines_model, except_check, except_product_ids, except_category_ids) {
                var total = 0;
                orderlines_model.forEach(function (line) {
                    console.log("lineline", line.product)
                    if (line.product.display_name != "POS-Coupon-Product") {
                        if (except_check == 'product') {
                            if (except_product_ids.includes(line.product.id)) {

                            } else {
                                total += (line.price * line.quantity)
                            }

                        } else if (except_check == 'category') {
                            if (except_category_ids.includes(line.product.categ_id[0])) {

                            } else {
                                total += (line.price * line.quantity)
                            }

                        } else {
                            total += (line.price * line.quantity)
                        }

                    }


                });
                return total;

            },
            get_total_order2: function (orderlines_model) {
                var total = 0;
                orderlines_model.forEach(function (line) {
                    if (line.product.display_name != "POS-Coupon-Product") {
                        total += (line.price * line.quantity)
                    }


                });
                return total;

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

        function get_coupon_product(products) {
            for (var i in products) {
                if (products[i]['display_name'] == 'POS-Coupon-Product')
                    return products[i]['id'];
            }
            return false;
        }


        class POSCouponPopupWidget extends AbstractAwaitablePopup {

            constructor() {
                super(...arguments);
                this.coupon_product = null;
                this.state = useState({
                    coupon_code: this.props.coupon_code,

                })


            }

            getPayload() {
                var selected_vals = [];
                var coupon_code = this.state.coupon_code;
                selected_vals.push(coupon_code);
                return selected_vals
            }

            mounted() {
                var self = this;
                if (!this.coupon_product)
                    this.coupon_product = get_coupon_product(self.env.pos.db.product_by_id);
                this.flag = true;
                //// console.log('self.coupon_product', this.coupon_product);
                if (this.coupon_product) {
                    this.render_coupon();
                } else {

                    self.trigger('close-popup');
                    self.showPopup('ErrorPopup', {
                        title: "Can not find coupoun product!",
                        body: "Coupon product name (POS-Coupon-Product) doesn't appear on pos"
                    });

                }
                $('input').focus();
            }

            click_confirm() {
                var payload = this.getPayload();
                var value = payload[0];
                this.trigger('close-popup');
                // if (this.options.confirm) {
                //     this.options.confirm.call(this, value);
                // }
            }


            render_coupon() {
                var self = this;
                $(".verify_coupon").click(function () {
                    // checking the code entered
                    var flag = true;
                    self.env.pos.refresh_coupons_data()
                    var order = self.env.pos.get_order();
                    // console.log("current_order", current_order)
                    var coupon = $("#coupon_code").val();

                    if (coupon) {
                        var coupon_stat = order.check_validity(coupon);
                        console.log("coupon", coupon_stat)
                        if (order.orderlines.models.length == 0) {
                            self.showPopup('ErrorPopup', {
                                title: "No products !",
                                body: "You cannot apply coupon without products."
                            });

                        } else if (coupon_stat && coupon_stat['coupon_res'] && coupon_stat['status']) {
                            console.log("coupon_stat['status']", coupon_stat['status'])
                            var coupon_res = coupon_stat['coupon_res'];
                            var coupon_line_data = {
                                'state': 'verified',
                                'coupon_id': coupon_res['id'],
                                'order_name': order.name,
                                'partner_id': order.get_client()['id']
                            }
                            var data = {
                                'coupon_id': coupon_res['id'],
                                'coupon_line_data': coupon_line_data
                            }
                            self.env.pos.update_pos_coupon_data_to_backend(data)
                            // console.log("coupon_res", coupon_res);
                            var discount_val = order.get_coupon_total_discount(coupon_res);
                            if (typeof discount_val !== 'object') {
                                if (discount_val <= 0) {
                                    if (self.env.pos.get_client()) {
                                        // var customer = self.pos.get_client();
                                        //// console.log("current_order.orderlines.models", current_order.orderlines.models)
                                        // is there a coupon with this code which has balance above zero
                                        // checking coupon balance and expiry
                                        flag = check_expiry(coupon_res['start_date'], coupon_res['end_date']);
                                        if (!flag) {
                                            $(".coupon_status_p").text("Unable to apply coupon. Check coupon validity.!");
                                        } else {
                                            $(".confirm-coupon").css("display", "block");
                                            var obj = $(".coupon_status_p").text("This Coupon gives you discount : " + discount_val * -1 + " \n" +
                                                " Do you want to proceed ? \n This operation cannot be reversed.");
                                            obj.html(obj.html().replace(/\n/g, '<br/>'));
                                            // var order = self.pos.get_order();
                                            // order.set_coupon_value(coupon_res);
                                        }
                                        // else{
                                        //     var ob = $(".coupon_status_p").text("Invalid code or no coupons left. \nPlease check coupon validity.\n" +
                                        //         "or check whether the coupon usage is limited to a particular customer.");
                                        //     ob.html(ob.html().replace(/\n/g,'<br/>'));
                                        // }
                                        self.flag = flag;
                                    } else {
                                        $(".coupon_status_p").text("Please select a customer !!");
                                    }
                                } else {
                                    flag = false;
                                    $(".coupon_status_p").text("Your items doesn't conatains product equal this coupon products.");
                                }
                            } else {
                                flag = false;
                                $(".coupon_status_p").text(discount_val['message']);
                            }
                        } else {
                            console.log("coupon", coupon_stat)
                            flag = false;
                            $(".coupon_status_p").text(coupon_stat['message']);
                        }
                    }

                });
                $(".confirm-coupon").click(function () {
                    // verifying and applying coupon
                    self.env.pos.refresh_coupons_data()
                    var coupon = $("#coupon_code").val();
                    var order = self.env.pos.get_order();
                    if (coupon) {
                        var coupon_stat = order.check_validity(coupon);
                        if (self.flag && coupon_stat['status'] && coupon_stat['coupon_res']) {
                            var coupon_res = coupon_stat['coupon_res'];
                            var coupon_data = {
                                'coupon_id': coupon_res['id']
                            }
                            self.env.pos.update_pos_coupon_data_to_backend(coupon_data)
                            var discount_val = order.get_coupon_total_discount(coupon_res);
                            // var lines = order.orderlines ? order : 0;
                            if (order.orderlines.models.length) {
                                var product = self.env.pos.db.get_product_by_id(self.coupon_product);
                                if ((order.get_total_with_tax - discount_val) <= 0) {
                                    self.trigger('close-popup');

                                    self.showPopup('ErrorPopup', {
                                        title: "Unable to apply Coupon !",
                                        body: "Coupon amount is too large to apply. The total amount cannot be negative"
                                    });

                                } else {
                                    order.add_product(product, {
                                        quantity: 1,
                                        price: discount_val
                                    });
                                    var partner_id = order.get_client()['id']
                                    var coupon_line_data = {
                                        'state': 'confirmed',
                                        'coupon_id': coupon_res['id'],
                                        'order_name': order.name,
                                        'partner_id': partner_id
                                    }
                                    var data = {
                                        'coupon_id': coupon_res['id'],
                                        'coupon_line_data': coupon_line_data
                                    }
                                    order.coupon_applied(partner_id, coupon_res);
                                    // order.coupon = coupon_res
                                    self.env.pos.update_pos_coupon_data_to_backend(data)
                                    order.coupon_id = coupon_res['id']
                                    self.trigger('close-popup');
                                    // updating coupon balance after applying coupon
                                }
                            } else {
                                self.trigger('close-popup');

                                self.showPopup('ErrorPopup', {
                                    title: "Unable to apply Coupon !",
                                    body: "Please select some products !"
                                });

                            }
                        } else {
                            self.trigger('close-popup');

                            self.showPopup('ErrorPopup', {
                                title: "Unable to apply Coupon !",
                                body: coupon_stat['message']
                            });
                        }
                    }
                });
            }


        }

        POSCouponPopupWidget
            .template = 'POSCouponPopupWidget';
        POSCouponPopupWidget
            .defaultProps = {
            title: 'Enter Your Coupon',
            body: '',
        };

        Registries
            .Component
            .add(POSCouponPopupWidget);

        return
        POSCouponPopupWidget;


    }
);
