odoo.define('aspl_pos_create_so_extension.PaymentScreenInherit', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const { posbus } = require('point_of_sale.utils');
    const { useRef, useState } = owl.hooks;

    const PaymentScreenInherit = (PaymentScreen) =>
        class extends PaymentScreen{
            constructor(){
                super(...arguments);
            }
            async validateSO(){
                var order = this.env.pos.get_order();
                var sale_order_id = order.get_sale_order_id();
                var location = this.env.pos.config.picking_type_id[0];
                var paymentlines = [];
                _.each(order.get_paymentlines(), function(paymentline){
                    paymentlines.push({
                    'journal_id': paymentline.payment_method.id,
                    'amount': paymentline.amount,
                    })
                });
                if(order.get_sale_order_pay()){
                     var params = {
                        model: 'sale.order',
                        method: 'pay_from_so_screen',
                        args: [{ "sale_order_id" : order.sale_order_id , "location": location,"paymentlines" : paymentlines }],
                     }
                     var result = await this.rpc(params);
                     if(result[0]){
                        var exist_invoice = _.findWhere(this.env.pos.db.get_invoices_list(), {'id': result[0].id})
                        if(exist_invoice){
                            _.extend(exist_invoice,result[0]);
                        }
                        this.env.pos.db.add_invoices(this.env.pos.db.get_invoices_list());
                     }
                     if(result[1]){
                        var exist_sale_order = _.findWhere(this.env.pos.db.get_orders_list(), {'id': result[1].id})
                        if(exist_sale_order){
                            _.extend(exist_sale_order,result[1]);
                        }
                        this.env.pos.db.add_orders(this.env.pos.db.get_orders_list());
                     }
                     this.showScreen('ReceiptScreen')
                }else{
                    this.showScreen('CreateSaleOrderScreen',{'operation' : 'direct_pay'});
                }
            }
            async payInvoice(){
                var order = this.env.pos.get_order();
                var paymentlines = [];
                _.each(order.get_paymentlines(), function(paymentline){
                    paymentlines.push({
                        'journal_id': paymentline.payment_method.id,
                        'amount': paymentline.amount,
                    })
                });
                var params = {
                    model: 'sale.order',
                    method: 'pay_invoice',
                    args: [{ "invoice_id" : order.get_invoice_id() , "paymentlines" : paymentlines }],
                }
                var paidInvoice = await this.rpc(params);
                if(paidInvoice){
                    var exist_invoice = _.findWhere(this.env.pos.db.get_invoices_list(), {'id': paidInvoice[0].id})
                    if(exist_invoice){
                        _.extend(exist_invoice,paidInvoice[0]);
                    }
                    this.env.pos.db.add_invoices(this.env.pos.db.get_invoices_list());
                    if(paidInvoice[1]){
                        var exist_sale_order = _.findWhere(this.env.pos.db.get_orders_list(), {'id': paidInvoice[1].id})
                        if(exist_sale_order){
                            _.extend(exist_sale_order,paidInvoice[1]);
                        }
                        this.env.pos.db.add_orders(this.env.pos.db.get_orders_list());
                    }
                    this.showScreen('ReceiptScreen')
                }
            }
            async payment_back(){
                if(this.env.pos.get_order().get_sale_order_mode()){
                    const { confirmed } = await this.showPopup('ConfirmPopup',{
                            title: this.env._t('Confirmation'),
                            body: this.env._t(
                                'Would you like to Discard this order?'
                            ),
                    });
                    if (confirmed){
                        this.env.pos.get_order().destroy({ reason: 'abandon' });
                        posbus.trigger('order-deleted');
                        this.showScreen('ProductScreen')
                    }
                }else{
                    this.showScreen('ProductScreen')
                }
            }

        }

    Registries.Component.extend(PaymentScreen, PaymentScreenInherit);

    return PaymentScreenInherit;

});
