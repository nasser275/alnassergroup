/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_order_backup.chrome', function (require) {
    "use strict";
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class OrderBackupWidget extends PosComponent {
        onClick() {
            this.showPopup("OrderBackupPopup");
        }
    }
    OrderBackupWidget.template = 'OrderBackupWidget';
    Registries.Component.add(OrderBackupWidget);
});