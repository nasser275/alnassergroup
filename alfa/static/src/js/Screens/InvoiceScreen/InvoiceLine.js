odoo.define('point_of_sale.InvoiceLine', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useState, useRef } = owl.hooks;
    const { useListener } = require('web.custom_hooks');

    class InvoiceLine extends PosComponent {
        constructor() {
            super(...arguments);
        }
        async printInvoice(invoice_id){
            try{
                await this.env.pos.do_action('account.account_invoices', {
                    additional_context: {
                        active_ids: [invoice_id],
                    },
                });
            }catch (error) {
                if (error instanceof Error) {
                    throw error;
                } else {
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Network Error'),
                        body: this.env._t('Unable to download invoice.'),
                    });
                }
            }
        }
        payInvoice(invoice){
            var selectedOrder = this.env.pos.get_order();
            selectedOrder.destroy();
            var selectedOrder = this.env.pos.get_order();
            if(this.env.pos.config.paid_amount_product){
                var partner_id = invoice.partner_id[0];
                var pay_amount = invoice.amount_residual;
                var invoice_name = invoice.name
                selectedOrder.set_invoice_id(invoice.id)
                var product = this.env.pos.db.get_product_by_id(this.env.pos.config.paid_amount_product[0]);
                var partner = this.env.pos.db.get_partner_by_id(partner_id)
                selectedOrder.add_product(product, {price: pay_amount, quantity: 1});
                selectedOrder.set_client(partner);
            }
            this.showScreen('PaymentScreen')
        }
    }
    InvoiceLine.template = 'InvoiceLine';

    Registries.Component.add(InvoiceLine);

    return InvoiceLine;
});
