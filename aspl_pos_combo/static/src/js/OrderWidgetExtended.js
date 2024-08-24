odoo.define('aspl_pos_combo.OrderWidgetExtended', function (require) {
    'use strict';

    const OrderWidget = require('point_of_sale.Orderline');
    const Registries = require('point_of_sale.Registries');
    const {Gui} = require('point_of_sale.Gui');

    const OrderWidgetExtended = (OrderWidget) =>
        class extends OrderWidget {
            on_click() {
            	var self=this;
                var product = this.props.line.product
                var combo_product_info = this.props.line.get_combo_prod_info()
                if (product.is_combo && product.product_combo_ids.length > 0 && self.env.pos.config.enable_combo) {
                	console.log("combo_product_info",product,this.props.line,combo_product_info)
                    Gui.showPopup('POSComboProductPopup', {
                        'product': product,
                        'combo_product_info': combo_product_info
                    });

                }
            }


        };

    Registries.Component.extend(OrderWidget, OrderWidgetExtended);

    return OrderWidget;

});