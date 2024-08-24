odoo.define('aspl_pos_create_so_extension.SaleOrderConfirmPopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    class SaleOrderConfirmPopup extends AbstractAwaitablePopup {}

    SaleOrderConfirmPopup.template = 'SaleOrderConfirmPopup';

    SaleOrderConfirmPopup.defaultProps = {
        confirmText: 'Download',
        title: 'Successful',
        cancelText: 'Close'
    };

    Registries.Component.add(SaleOrderConfirmPopup);

    return SaleOrderConfirmPopup;
});
