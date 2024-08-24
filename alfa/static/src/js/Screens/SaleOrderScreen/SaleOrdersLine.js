odoo.define('point_of_sale.SaleOrdersLine', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useState, useRef } = owl.hooks;
    const { useListener } = require('web.custom_hooks');
    var rpc = require('web.rpc');

    class SaleOrdersLine extends PosComponent {
        constructor(){
            super(...arguments);
        }
        async editOrder(order_id){
            var selectedOrder = this.env.pos.get_order();
            selectedOrder.destroy();
            var selectedOrder = this.env.pos.get_order();
            var sale_order = this.env.pos.db.get_order_by_id(order_id);
            if (sale_order.partner_id){
                var partner = this.env.pos.db.get_partner_by_id(sale_order.partner_id)
                selectedOrder.set_client(partner ? partner : null);
            }
            var params = {
                model: 'sale.order.line',
                method: 'search_read',
                domain: [['order_id', '=', order_id]],
            }
            let SaleOrderLines = await this.rpc(params);
            var self = this;
            _.each(SaleOrderLines, function(line){
                var product = self.env.pos.db.get_product_by_id(Number(line.product_id[0]));
                if(product){
                    selectedOrder.add_product(product,{
                        quantity: line.product_uom_qty,
                        discount: line.discount,
                        price: line.price_unit,
                    })
                }
            });
            selectedOrder.set_is_quotation(true);
            selectedOrder.set_sale_order_id(order_id);
            selectedOrder.set_sale_order_id_to_edit(order_id);
            this.showScreen('ProductScreen');
        }
        async payOrder(order_id){
            var selectedOrder = this.env.pos.get_order();
            selectedOrder.destroy();
            var selectedOrder = this.env.pos.get_order();
            let sale_order = this.env.pos.db.get_order_by_id(order_id);
            if (sale_order.partner_id){
                let partner = this.env.pos.db.get_partner_by_id(sale_order.partner_id);
                selectedOrder.set_client(partner ? partner : null);
            }
            let product = this.env.pos.db.get_product_by_id(this.env.pos.config.paid_amount_product[0]);
            selectedOrder.add_product(product, {price: sale_order.amount_due, quantity: 1});
            selectedOrder.set_sale_order_id(order_id);
            selectedOrder.set_sale_order_pay(true);
            this.showScreen('PaymentScreen');
        }
        async returnOrder(order_id){
            var self = this;
            if(order_id){
                var sale_order = self.env.pos.db.get_order_by_id(order_id);
                if(sale_order){
                    var params = {
                        model: "sale.order",
                        method: "get_return_product",
                        args: [order_id]
                    }
                    rpc.query(params, {async: false}).then(async function(result){
                        if(result && result[0]){
                            var flag = false;
                            result.map(function(line){
                                if(line.qty > 0){
                                    flag = true;
                                }
                            });
                            if(flag){
                                const { confirmed, payload } = await self.showPopup('SaleOrderReturnPopup', {
                                      'lines':result,
                                      'sale_order':sale_order
                                });
                                if(confirmed){
                                    var filter_records = [];
                                    _.each(payload, function(line){
                                        if(line.return_qty > 0){
                                            filter_records.push(line)
                                        }
                                    });
                                    if(filter_records){
                                        var params = {
                                            model: 'sale.order',
                                            method: 'return_sale_order',
                                            args: [filter_records],
                                        }
                                        rpc.query(params, {async: false}).then(function(result){
                                            if(result){
                                                alert("Sale order return successfully!");
                                                self.trigger('close-popup');
                                            }
                                        });
                                    }
                                }
                            }else{
                                alert("Sorry, No items available for return sale order!");
                            }
                        }else{
                            alert("Sorry, No items available for return sale order!");
                        }
                    });
                }
            }
        }
    }
    SaleOrdersLine.template = 'SaleOrdersLine';

    Registries.Component.add(SaleOrdersLine);

    return SaleOrdersLine;
});
