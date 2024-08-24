odoo.define('aspl_pos_combo.combo_pop', function (require) {
    "use strict";


    const Registries = require('point_of_sale.Registries');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const {
        useListener
    } = require('web.custom_hooks');

    const {
        useState,
        useRef
    } = owl.hooks;


    class POSComboProductPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
             this.state = useState({
                product: this.props.product,
                combo_product_info: this.props.combo_product_info,
                test: this.props.test,
            })
            this.new_combo_products_details=[]
        }
        getPayload() {

        }
        mounted() {
            $('.combo_header2_body').scrollTop(this.scroll_position);
            this.show()


        }
        collaps_div(event) {
            if ($(event.currentTarget).hasClass('fix_products')) {
                $('.combo_header_body').slideToggle('500');
                $(event.currentTarget).find('i').toggleClass('fa-angle-down fa-angle-up');
            } else if ($(event.currentTarget).hasClass('selective_products')) {
                $('.combo_header2_body').slideToggle('500');
                $(event.currentTarget).find('i').toggleClass('fa-angle-down fa-angle-up');
            }
        }
        select_product(event) {
            var self = this;
            var $el = $(event.currentTarget);
            var product_id = Number($el.data('product-id'));
            var category_id = Number($el.data('categ-id'));
            var line_id = Number($el.data('line-id'));
            self.scroll_position = Number($('.combo_header2_body').scrollTop()) || 0;
            if ($(event.target).hasClass('fa-times') || $(event.target).hasClass('product-remove')) {
                if ($el.hasClass('selected')) {
                    self.new_combo_products_details.map(function(combo_line) {
                        if (!combo_line.require) {
                            if (combo_line.id == line_id && (combo_line.pos_category_id[0] == category_id || (_.contains(combo_line.product_ids, product_id)))) {
                                combo_line.product_details.map(function(product_detail) {
                                    if (product_detail.product_id == product_id) {
                                        self.state.test=product_detail.used_time
                                        product_detail.used_time = 0;
                                    }
                                });
                            }
                        }
                    });
                }
            }
            else {
                self.new_combo_products_details.map(function(combo_line) {
                    if (!combo_line.require) {
                        if (combo_line.id == line_id && (combo_line.pos_category_id[0] == category_id || (_.contains(combo_line.product_ids, product_id)))) {

                            var added_item = 0;
                            var products_quantity = self.env.pos.products_quantity;
                            combo_line.product_details.map(function(product_detail) {
                                added_item += product_detail.used_time;
                                self.state.test=product_detail.used_time

                            });
                            combo_line.product_details.map(function(product_detail) {
                                if (product_detail.product_id == product_id) {
                                    if (product_detail.no_of_items > product_detail.used_time && product_detail.no_of_items > added_item) {
                                        product_detail.used_time += 1;
                                         self.state.test=product_detail.used_time
                                    }
                                    var product_qty = products_quantity[(product_detail.product_id).toString()] ? products_quantity[(product_detail.product_id).toString()].quantity : 0;
                                    console.log("Prod ID",product_detail.product_id)
                                    console.log("Prod QTY",product_qty)
                                    console.log("Prod Used Time",product_detail.used_time)
                                    if(product_qty < product_detail.used_time){


                                        self.showPopup('ErrorPopup', {
                                                    title: self.env._t('Out Of Stock'),
                                                    body: self.env._t(" الكمية المتاحة من ," + " (" + products_quantity[(product_detail.product_id).toString()].product_id[1] + ") " + product_detail.used_time + " قطعة "),

                                                });
                                                self.click_cancel()
                                    }
                                }
                            });
                        }
                    }
                });
            }

        }
        click_cancel() {
            var order = this.env.pos.get_order();
            var selected_line = order.get_selected_orderline();
            if (selected_line && !selected_line.get_combo_prod_info()) {
                order.remove_orderline(selected_line);
            }
            this.trigger('close-popup');
        }
        click_confirm() {
            var self = this;
            var order = self.env.pos.get_order();
            var total_amount = 0;
            // var combo_cost = 0;
            var products_info = [];
            var pricelist = order.pricelist;
            var flag_selected = false;
            self.new_combo_products_details.map(function(combo_line) {
                var selected_products = 0;
                if (combo_line.product_details.length > 0) {
                    combo_line.product_details.map(function(prod_detail) {
                        if (prod_detail.used_time) {
                            selected_products += prod_detail.used_time
                            var product = self.env.pos.db.get_product_by_id(prod_detail.product_id);
                            var products_quantity = self.env.pos.products_quantity;
                            if (product) {
                                total_amount += prod_detail.used_time * ((product.get_price(pricelist, 1) - product.get_price(pricelist, 1) * (combo_line.discount / 100)));
                                // combo_cost += product.standard_price
                                products_info.push({
                                    "product": product,
                                     'product_name': product.display_name,
                                    'qty': prod_detail.used_time,
                                    'price': product.get_price(pricelist, 1),
                                    'id': combo_line.id,
                                    'discount': combo_line.discount,
                                    "combo_name": self.product.display_name,
                                     'tax':product.taxes_id.length>0 ? true : false ,
                                     'price_w_o_tax':(product.price_w_o_tax*prod_detail.used_time)*(1-(combo_line.discount/100))
                                });
                                console.log("Produccct 1", product.id)
                                // products_quantity[(product.id).toString()].quantity -= prod_detail.used_time;
                            }
                        }
                    });
                }
                if (combo_line.no_of_items > selected_products) {
                    flag_selected = true;
                }
            });
            if (flag_selected) {
                this.showPopup('ErrorPopup', {
                    'title': 'Check Selected Quantity',
                    'body': 'Please Select Anthor Products',
                });
                var selected_line = order.get_selected_orderline();
                console.log("D>>D>D",selected_line)
                order.remove_orderline(selected_line);
                return false;

            } else {
                var selected_line = order.get_selected_orderline();
                if (products_info.length > 0) {
                    if (selected_line) {
                        //            		selected_line.set_unit_price(total_amount);
                        selected_line.set_combo_prod_info(products_info);
                        // Code Change for Print Combo in Kitchen Screen
                        var combo_order_line = selected_line;
                        order.remove_orderline(selected_line);
                        var combo_product = self.env.pos.db.get_product_by_id(Number(combo_order_line.product.id));
                        order.add_product(combo_product, {
                            quantity: combo_order_line.quantity,
                            price: total_amount,
                        });
                        var new_line = order.get_selected_orderline();
                        new_line.set_combo_prod_info(combo_order_line.combo_prod_info);
                        new_line.combo_cost = this.product.combo_cost
                        // new_line.combo_price = this.product.lst_price
                        new_line.combo_price = this.product.combo_price
                        // new_line.price_unit = total_amount
                        new_line.price_manually_set = true;
                        new_line.set_unit_price(total_amount);
                    } else {
                        alert("Selected line not found!");
                    }
                } else {
                    if (selected_line && !selected_line.get_combo_prod_info()) {
                        order.remove_orderline(selected_line);
                    }
                }

                this.trigger('close-popup');
            }

        }
        show() {
            var self = this;
            this.product = this.state.product || false;
            this.combo_product_info = this.state.combo_product_info || false;
            var combo_products_details = [];
            self.state.new_combo_products_details = [];
            var new_combo_products_details_list = [];
            this.scroll_position = 0;
            var  product_ids2=[];
            this.product.product_combo_ids.map(function(id) {
                var record = _.find(self.env.pos.product_combo, function(data) {
                    return data.id === id;
                });
                combo_products_details.push(record);
            });
            combo_products_details.map(function(combo_line) {
                var details = [];
                if (combo_line.product_ids.length > 0) {

                    combo_line.product_ids.map(function(product_id) {
                        if (self.env.pos.db.get_product_by_id(product_id)) {
                            product_ids2.push(product_id)
                            if (combo_line.require) {
                            var data = {
                                'no_of_items': combo_line.no_of_items,
                                'product_id': product_id,
                                'category_id': combo_line.pos_category_id[0] || false,
                                'used_time': combo_line.no_of_items,
                            }
                            details.push(data);
                        } else {

                            var data = {
                                'no_of_items': combo_line.no_of_items,
                                'product_id': product_id,
                                'category_id': combo_line.pos_category_id[0] || false,
                                'used_time': 0
                            }
                            if (self.combo_product_info) {
                                self.combo_product_info.map(function(line) {
                                    if (combo_line.id == line.id && line.product.id == product_id) {
                                        data['used_time'] = line.qty;
                                    }
                                });
                            }
                            details.push(data);
                        }
                        }
                    });
                    new_combo_products_details_list.push(
                        {
                        'id': combo_line.id,
                        'no_of_items': combo_line.no_of_items,
                        'pos_category_id': combo_line.pos_category_id,
                        'product_details': details,
                        'product_ids': product_ids2,
                        'require': combo_line.require,
                        'discount': combo_line.discount,
                    }
                    )
                }
            });
            self.new_combo_products_details=new_combo_products_details_list;

        }
        get_image(prd){
            var product_image_url = `/web/image?model=product.product&field=image_128&id=${prd.id}&write_date=${prd.write_date}&unique=1`;
            return product_image_url
        }




    }

    POSComboProductPopup.template = 'POSComboProductPopup';
    POSComboProductPopup.defaultProps = {
        confirmText: 'Apply',
        cancelText: 'Cancel',
        title: 'Combo Product',
        body: '',
    };

    Registries.Component.add(POSComboProductPopup);
    return POSComboProductPopup;


});