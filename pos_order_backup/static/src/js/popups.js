/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_order_backup.popups', function (require) {
    "use strict";
	const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    class OrderBackupPopup extends AbstractAwaitablePopup {
        backup_cache(event){
            this.env.pos.db.download_cached_orders(this.env.pos.pos_session.name.toString());
            this.show_third_set();
        }
        show_third_set(){
            $(".backup-popup-one").hide();
            $(".backup-popup-three").show();
        }
        clear_cache(event){
            this.show_second_set();
        }
        show_second_set(){
            $(".backup-popup-one").hide();
            $(".backup-popup-two").show();
        }
        confirm_clear_cache(event){
            this.env.pos.db.clear_cached_orders();
            this.env.pos.push_orders(null,{'show_error':true});
            this.cancel();
        }
    }
    OrderBackupPopup.template = 'OrderBackupPopup';
	Registries.Component.add(OrderBackupPopup);
});