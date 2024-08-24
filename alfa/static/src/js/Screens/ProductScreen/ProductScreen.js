odoo.define('aspl_pos_create_so_extension.ProductScreenInh', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    var rpc = require('web.rpc');
    const Registries = require('point_of_sale.Registries');
    const { useRef, useState } = owl.hooks;

    const ProductScreenInh = (ProductScreen) =>
        class extends ProductScreen{
            constructor(){
                super(...arguments);
            }
            async _onClickPay(){
                if(this.env.pos.get_order().get_sale_order_mode()){
                    if(this.env.pos.user.sale_order_operations != 'paid'){
                        await this.showErrorPopup();
                    }else if(!this.env.pos.get_client()){
                        confirm('Please Select Client!');
                        return;
                    }else if(this.env.pos.get_order().get_is_quotation()){
                        await this.showErrorPopup();
                    }else if(!this.env.pos.get_order().get_orderlines().length > 0){
                        confirm('Please Select Product!');
                        return;
                    }else{
                        this.showScreen('PaymentScreen');
                    }
                }else if(!this.env.pos.get_order().get_sale_order_mode()){
                    if(this.env.pos.get_order().get_is_quotation()){
                        await this.showErrorPopup();
                    }else{
                        this.showScreen('PaymentScreen');
                    }
                }else{
                    this.showScreen('PaymentScreen');
                }
            }
            async showErrorPopup(){
                await this.showPopup('ErrorPopup', {
                    title: this.env._t('Error'),
                    body: this.env._t(
                        "You don't have access rights to proceed further !!"
                    ),
                });
            }
        }

    Registries.Component.extend(ProductScreen, ProductScreenInh);

    return ProductScreenInh;
});
