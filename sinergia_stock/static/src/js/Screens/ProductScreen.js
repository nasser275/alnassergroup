// BiProductScreen js
odoo.define('bi_pos_stock.productScreen', function (require) {
    "use strict";

    const Registries = require('point_of_sale.Registries');
    const ProductScreen = require('point_of_sale.ProductScreen');

    const BiProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            constructor() {
                super(...arguments);
            }

            async _clickProduct(event) {
                let self = this;
                let order = this.env.pos.get_order();
                let lines = order.get_orderlines();
                const product = event.detail;
                let qqty = 0
                $.each(lines, function (i, line) {
                    if (line.product.id == product.id) {
                        qqty += line.quantity


                    }
                });
                let allow_order = self.env.pos.config.pos_allow_order;
                let deny_order = self.env.pos.config.pos_deny_order;
                let call_super = true;
                if (self.env.pos.config.pos_display_stock) {
                    if (self.env.pos.config.show_stock_location == 'specific' && product.type == 'product') {
                        var partner_id = self.env.pos.get_client();
                        var location = self.env.pos.locations;
                        await this.rpc({
                            model: 'stock.quant',
                            method: 'get_single_product',
                            args: [partner_id ? partner_id.id : 0, product.id, location],
                        }).then(function (output) {
                            if (allow_order == false) {
                                if ((output[0][1] <= qqty) || (output[0][1] <= 0)) {
                                    call_super = false;
                                    self.showPopup('ErrorPopup', {
                                        title: self.env._t('Out Of Stock'),
                                        body: self.env._t(" الكمية المتاحة من ," + " (" + product.display_name + ") " + qqty + " قطعة "),

                                    });
                                }
                            } else if (allow_order == true) {
                                if (output[0][1] <= qqty) {
                                    call_super = false;
                                    self.showPopup('ErrorPopup', {
                                        title: self.env._t('Out Of Stock'),
                                        body: self.env._t(" الكمية المتاحة من ," + " (" + product.display_name + ") " + qqty + " قطعة "),

                                    });
                                }
                            }
                        });
                    } else {
                        if (product.type == 'product' && allow_order == false) {
                            if (product.qty_available <= qqty && allow_order == false) {
                                call_super = false;
                                self.showPopup('ErrorPopup', {
                                    title: self.env._t('Out Of Stock'),
                                    body: self.env._t(" الكمية المتاحة من ," + " (" + product.display_name + ") " + qqty + " قطعة "),

                                });
                            } else if (product.qty_available <= 0 && allow_order == false) {
                                call_super = false;
                                self.showPopup('ErrorPopup', {
                                    title: self.env._t('Out Of Stock'),
                                    body: self.env._t(" الكمية المتاحة من ," + " (" + product.display_name + ") " + 0 + " قطعة "),

                                });
                            }
                        } else if (product.type == 'product' && allow_order == true && product.qty_available <= qqty) {
                            call_super = false;
                            self.showPopup('ErrorPopup', {
                                title: self.env._t('Out Of Stock'),
                                body: self.env._t(" الكمية المتاحة من ," + " (" + product.display_name + ") " + 0 + " قطعة "),

                            });
                        }
                    }
                }
                if (call_super) {
                    super._clickProduct(event);
                }
            }

            async _onClickPay() {
                var self = this;
                let order = this.env.pos.get_order();
                let lines = order.get_orderlines();
                let pos_config = self.env.pos.config;
                let allow_order = pos_config.pos_allow_order;
                let deny_order = pos_config.pos_deny_order;
                let call_super = true;
                if (pos_config.pos_display_stock) {
                    if (pos_config.show_stock_location == 'specific') {
                        let partner_id = self.env.pos.get_client();
                        let location = self.env.pos.locations;
                        let prods = [];

                        $.each(lines, function (i, line) {
                            if (line.product.type == 'product') {
                                prods.push(line.product.id)
                            }
                        });
                        await this.rpc({
                            model: 'stock.quant',
                            method: 'get_products_stock_location_qty',
                            args: [partner_id ? partner_id.id : 0, location, prods],
                        }).then(function (output) {
                            var flag = 0;
                            for (var i = 0; i < lines.length; i++) {
                                for (var j = 0; j < output.length; j++) {
                                    var values = $.map(output[0], function (value, key) {
                                        var keys = $.map(output[0], function (value, key) {
                                            if (lines[i].product.type == 'product' && lines[i].product['id'] == key) {
                                                if (allow_order == false && lines[i].quantity > value) {
                                                    flag = flag + 1;
                                                }
                                                var check = value - lines[i].quantity;
                                                if (allow_order == true && deny_order > check) {
                                                    flag = flag + 1;
                                                }
                                            }
                                        });
                                    });
                                }
                            }
                            if (flag > 0) {
                                call_super = false;
                                self.showPopup('ErrorPopup', {
                                    title: self.env._t('Out Of Stock'),
                                    body: self.env._t('One or more products in the order are out of stock. '),
                                });
                            }
                        });
                    } else {
                        $.each(lines, function (i, line) {
                            if (line.product.type == 'product') {
                                if (allow_order == false && line.quantity > line.product['bi_on_hand']) {
                                    call_super = false;
                                    self.showPopup('ErrorPopup', {
                                        title: self.env._t('Out Of Stock'),
                                        body: self.env._t('One or more products in the order are out of stock. '),
                                    });
                                    return
                                }
                                var check = line.product['bi_on_hand'] - line.quantity;
                                if (allow_order == true && check < deny_order) {
                                    call_super = false;
                                    self.showPopup('ErrorPopup', {
                                        title: self.env._t('Out Of Stock'),
                                        body: self.env._t('One or more products in the order are out of stock. '),
                                    });
                                    return
                                }
                            }
                        });
                    }
                }
                if (call_super) {
                    super._onClickPay();
                }
            }
        };

    Registries.Component.extend(ProductScreen, BiProductScreen);

    return ProductScreen;

});
