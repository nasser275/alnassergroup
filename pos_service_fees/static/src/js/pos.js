
odoo.define("pos_service_fees.ProductScreen", function (require) {
	"use strict";

	const {
		_t
	} = require('web.core');
	const ProductScreen = require('point_of_sale.ProductScreen');
	const {
		useListener
	} = require('web.custom_hooks');
	const Registries = require('point_of_sale.Registries');
	var rpc = require('web.rpc');
	const NumberBuffer = require('point_of_sale.NumberBuffer');
	    var models = require('point_of_sale.models');

var rpc = require('web.rpc');


	const PosProductScreen = (ProductScreen) =>
		class extends ProductScreen {
		add_Service_product(){
		if (this.env.pos.config.enable_service){
               var product = this.env.pos.db.get_product_by_id(this.env.pos.config.service_product_id[0]);
                var order = this.env.pos.get_order();
                 var lines  = order.get_orderlines();
                for (const line of lines) {
                    if (line.get_product() === product) {
                        order.remove_orderline(line);
                    }
                }
                order.add_product(product);


            }
		}

		 async _clickProduct(event) {
            var self = this;
            super._clickProduct(event)
            self.add_Service_product()

		}
		 async _barcodeProductAction(code) {
                var self = this;
                 super._barcodeProductAction(code);
                 self.add_Service_product()
            }

		}

	Registries.Component.extend(ProductScreen, PosProductScreen);

	return ProductScreen;
});

