odoo.define('point_of_sale.SignatureWidget', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useState, useRef } = owl.hooks;
    const { useListener } = require('web.custom_hooks');

    class SignatureWidget extends PosComponent {
        constructor() {
            super(...arguments);
            this.state = useState({ SignedBy: '', SignedOn: moment().format('YYYY-MM-DD')})
        }
        async mounted(){
            if(this.env.pos.get_order().get_raw_sign()){
                $('#signature_canvas').jSignature();
                let signData = this.env.pos.get_order().get_raw_sign();
                $('#signature_canvas').jSignature('setData', 'data:' + signData.join(','));
            }
            else{
                $('#signature_canvas').jSignature();
            }
        }
        captureChange(){
             this.trigger('update-signature-fields',{'SignedBy': this.state.SignedBy,'SignedOn': this.state.SignedOn})
        }
        clear(){
            this.env.pos.get_order().set_sign(null);
            this.env.pos.get_order().get_raw_sign(null);
            $("#signature_canvas").jSignature("reset");
        }
        applySign(){
            var order = this.env.pos.get_order();
            order.set_raw_sign($("#signature_canvas").jSignature("getData", "base30"));
            order.set_sign($("#signature_canvas").jSignature("getData", "image")[1]);
        }
    }
    SignatureWidget.template = 'SignatureWidget';

    Registries.Component.add(SignatureWidget);

    return SignatureWidget;
});
