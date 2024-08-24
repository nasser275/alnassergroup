odoo.define('point_of_sale.NoteWidget', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useState, useRef } = owl.hooks;
    const { useListener } = require('web.custom_hooks');

    class NoteWidget extends PosComponent {
        constructor() {
            super(...arguments);
            this.state = useState({ Note: ''})
        }
        captureChange(){
            this.trigger('update-order-note',{'orderNote': this.state.Note})
//            this.props.orderNote = this.props.orderNote;
        }
    }
    NoteWidget.template = 'NoteWidget';

    Registries.Component.add(NoteWidget);

    return NoteWidget;
});
