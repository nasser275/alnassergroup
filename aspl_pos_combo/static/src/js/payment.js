odoo.define('aspl_pos_combo.payment2', function (require) {
    "use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const {Gui} = require('point_of_sale.Gui');
    const L10nCoPosPaymentScreen = PaymentScreen =>
        class extends PaymentScreen {
            async _isOrderValid(isForceValidate) {
                var self = this;
                var flag = true;
                var flag2 = true;
                var st = "";
                var st2 = "";
                var order = this.env.pos.get_order();
                var lines = order.get_orderlines();
                var products_quantity = self.env.pos.products_quantity;
                for (const line of lines) {

                    if (line.product.is_combo && line.get_combo_prod_info()) {
                        for (const line2 of line.get_combo_prod_info()) {
                            var product_qty = products_quantity[(line2.product.id).toString()] ? products_quantity[(line2.product.id).toString()].quantity : 0;
                            if (product_qty < line.quantity * line2.qty) {
                                flag2 = false;
                                st2+=line2.product.display_name+","
                            }else{
                                console.log(">D>DD>D", products_quantity[(line2.product.id).toString()].quantity)
                                products_quantity[(line2.product.id).toString()].quantity -= (line.quantity * line2.qty);
                            }
                        }
                    }


                    if (line.product.is_combo && line.get_combo_prod_info() == false) {
                        flag = false;
                        st += line.product.display_name + ","
                    }
                }
                if (flag && flag2) {
                    return super._isOrderValid(...arguments);
                } else {
                    if (flag==false){
                         self.showPopup('ErrorPopup', {
                        title: self.env._t('Combo Not Have Products'),
                        body: self.env._t("Combo Not Have Products in " + st),

                    });
                    }
                    if(flag2==false){
                         self.showPopup('ErrorPopup', {
                        title: self.env._t('Out Of Stock'),
                        body: self.env._t("الكمية غير متاحة  للمنتجات " + st2),

                    });
                    }


                }


            }
        };

    Registries.Component.extend(PaymentScreen, L10nCoPosPaymentScreen);

    return PaymentScreen;


});
