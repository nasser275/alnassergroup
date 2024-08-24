odoo.define('pos_delivery_service.delivery_service_button', function (require) {
    "use strict";
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const {useListener} = require('web.custom_hooks');
    const {Gui} = require('point_of_sale.Gui');
    let core = require('web.core');
    let _t = core._t;

    class DeliveryButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.button_click);
        }

        async button_click() {
            var self=this;
            var order = this.env.pos.get_order();
            if (!order.get_client()) {
                const {confirmed} = await this.showPopup('ConfirmPopup', {
                    title: this.env._t('Unknown customer'),
                    body: this.env._t(
                        'You cannot use Home Delivery. Select customer first.'
                    ),
                });
                if (confirmed) {
                    self.selectClient();
                }
                return;
            }
            if (order.get_client()) {
                if (!order.get_client().phone) {
                const { confirmed } = await this.showPopup('ConfirmPopup', {
                    title: this.env._t('Please add phone for this customer'),
                    body: this.env._t(
                        'You need to add phone for  this customer before you can invoice or ship an order.'
                    ),
                });
                if (confirmed) {
                    this.selectClient();
                }
                return false;
            }
                    }
            var orderlines = order.orderlines.models;
            if (orderlines.length < 1) {
                this.showPopup('ErrorPopup', {
                    'title': _t('Empty Order !'),
                    'body': _t('Please select some products'),
                });
                return false;
            }

            var lines_without_qty = _.filter(
                    this.env.pos.get_order().get_orderlines(),
                    function (line) {
                        return line.quantity === 0;
                    }
                );
            if (lines_without_qty.length > 0) {
                    this.showScreen("ProductScreen");
                    Gui.showPopup("ConfirmPopup", {
                        title: _t("Missing quantities"),
                        body:
                            _t("No quantity set for products:") +
                            "\n" +
                            _.map(lines_without_qty, function (line) {
                                return " - " + line.product.display_name;
                            }).join("\n"),
                    });
                    return false;
                }

            var delivery_amount=order.delivery_amount;
            if (order.free_delivery){
                delivery_amount=0;
            }
            console.log(">>>",order.delivery_person_id)
            Gui.showPopup('DeliveryOrderWidget', {
                'delivery_person_id': order.delivery_person_id,
                'delivery_amount': delivery_amount,
                'free_delivery': order.free_delivery,
            });

        }
                async selectClient() {
        	var order = this.env.pos.get_order();
            // IMPROVEMENT: This code snippet is repeated multiple times.
            // Maybe it's better to create a function for it.
            const currentClient = order.get_client();
            const { confirmed, payload: newClient } = await this.showTempScreen(
                'ClientListScreen',
                { client: currentClient }
            );
            if (confirmed) {
                order.set_client(newClient);
                order.updatePricelist(newClient);
            }
        }



    }


    DeliveryButton.template = 'DeliveryButton';
    ProductScreen.addControlButton({

        component: DeliveryButton,
        'condition': function () {
            return this.env.pos.config.enable_delivery_service;
        },
    });

    Registries.Component.add(DeliveryButton);

    return DeliveryButton;


});