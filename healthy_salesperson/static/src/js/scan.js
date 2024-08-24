odoo.define("healthy_salesperson.scansales", function (require) {
    "use strict";

    var models = require("point_of_sale.models");
    const { Gui } = require("point_of_sale.Gui");
    const ProductScreen = require("point_of_sale.ProductScreen");
    const Registries = require("point_of_sale.Registries");

    const ShProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            async _barcodeProductAction(code) {
                var self = this;
                if (!this.get_salesperson(code)){
                super._barcodeProductAction(code)
                }


            }
            get_salesperson(barcode){
            if (barcode) {
                for (const item of this.env.pos.salespersons) {
                    if (item.barcode==barcode.code) {
                        this.env.pos.get_order().sales_person=item.id
                        return true
                    }
                }
            }

            }
        };
    Registries.Component.extend(ProductScreen, ShProductScreen);

});
