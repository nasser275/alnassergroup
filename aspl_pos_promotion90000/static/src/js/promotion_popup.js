odoo.define('aspl_pos_promotion.promotion_popup', function (require) {
    "use strict";

    const Registries = require('point_of_sale.Registries');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    var core = require('web.core');
    var QWeb = core.qweb;

    class PromotionWidget extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);

        }

        mounted() {
            var self = this;
            console.log(this.props.products)
            this.render_product_list(this.props.products);
            // $('div.gift-dialog').show()
            setTimeout(function () {
                $('div.promotion-dialog').removeClass('oe_hidden');
            }, 100);
            $('.clk_product_prom').click(function () {
                self._on_click_product(event)
            });
        }



        _on_click_product(event) {
            var self = this;
            var tr = $(event.currentTarget).closest('tr');
            var product_id = parseInt(tr.attr('id'));
            var products_quantity = self.env.pos.products_quantity;
             var product_qty = products_quantity[(product_id).toString()] ? products_quantity[(product_id).toString()].quantity : 0
              if (product_qty> 1) {
                    console.log('parseInt($(this).attr("id"))', product_id);
            var product = self.env.pos.db.get_product_by_id(product_id);
            self.env.pos.get_order().add_product(product, {
                quantity: 1,
                merge: false,
            });
            tr.css("background-color", "green");
              }else{
                         self.showPopup('ErrorPopup', {
                        title: self.env._t('Out Of Stock'),
                            body: self.env._t(" الكمية المتاحة  "+product_qty.toString() ),

                    });

              }

        }

        render_product_list(products) {
            var self = this;
            var contents = this.el.querySelector('.product_list');
            contents.innerHTML = "";
            for (var i = 0, len = products.length; i < len; i++) {
                var product = products[i];
                if (1 == 1) {
                    var product_html = QWeb.render('promo_product_row', {
                        widget: this,
                        product: product
                    });
                    product = document.createElement('tbody');
                    product.innerHTML = product_html;
                    product = product.childNodes[2];
                    contents.appendChild(product);
                }
            }
        }
    }

    PromotionWidget.template = 'PromotionWidget';
    PromotionWidget.defaultProps = {
        title: 'Promotion Products',
        body: '',
    };

    Registries.Component.add(PromotionWidget);
    return PromotionWidget;


});