odoo.define('pos_vib_customer.pos', function (require) {
    "use strict";

    var models = require('point_of_sale.models');


    models.load_fields('res.partner', ['is_vib']);
    models.load_fields('product.pricelist', ['is_vib']);

    models.Order = models.Order.extend({
        set_client: function (client) {
            this.assert_editable();
            this.set('client', client)
            //check if partner is is vib
            if (client) {
                if (client.is_vib) {

                    var vib_pricelist = _.find(this.pos.pricelists, function (pricelist) {
                        return pricelist.is_vib === true;
                    });
                    console.log("F>>>", vib_pricelist, this.pos.pricelists)
                    if (vib_pricelist) {
                        this.set_pricelist(vib_pricelist);
                    }

                } else {
                    this.set_pricelist(this.pos.default_pricelist);
                }
            } else {
                this.set_pricelist(this.pos.default_pricelist);
            }
        },
        updatePricelist: function (newClient) {
            let newClientPricelist, newClientFiscalPosition;
            const defaultFiscalPosition = this.pos.fiscal_positions.find(
                (position) => position.id === this.pos.config.default_fiscal_position_id[0]
            );
            if (newClient) {
                newClientFiscalPosition = newClient.property_account_position_id
                    ? this.pos.fiscal_positions.find(
                        (position) => position.id === newClient.property_account_position_id[0]
                    )
                    : defaultFiscalPosition;
                newClientPricelist =
                    this.pos.pricelists.find(
                        (pricelist) => pricelist.id === newClient.property_product_pricelist[0]
                    ) || this.pos.default_pricelist;
            } else {
                newClientFiscalPosition = defaultFiscalPosition;
                newClientPricelist = this.pos.default_pricelist;
            }
            this.fiscal_position = newClientFiscalPosition;
            if (newClient) {
                if (newClient.is_vib) {

                    var vib_pricelist = _.find(this.pos.pricelists, function (pricelist) {
                        return pricelist.is_vib === true;
                    });
                    if (vib_pricelist) {
                        this.set_pricelist(vib_pricelist);
                    }

                } else {
                    this.set_pricelist(newClientPricelist);
                }
            } else {
                this.set_pricelist(newClientPricelist);
            }

        },


    });

});