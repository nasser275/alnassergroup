odoo.define('print_pos_session.session', function (require) {
    "use strict";
    var ClosePosPopup = require('point_of_sale.ClosePosPopup');
    const Registries = require('point_of_sale.Registries');
    const rpc = require('web.rpc');

    const CustomClosePosPopup = (ClosePosPopup) =>
        class extends ClosePosPopup {
            printSession() {
                if (this.hasDifference()) {
                    return
                } else {
                    var self = this;
                    return rpc.query({
                        model: 'pos.session',
                        method: 'print_pdf',
                        args: [self.env.pos.pos_session.id],
                    }).then(function (data) {
                        self.env.pos.do_action(data);
                    });
                }

            }


        };

    Registries.Component.extend(ClosePosPopup, CustomClosePosPopup);

    return {ClosePosPopup};

});
