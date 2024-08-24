odoo.define('aspl_pos_create_so_extension.PopupProductLines', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const { useState, useRef } = owl.hooks;

    class PopupProductLines extends PosComponent {
        constructor() {
            super(...arguments);
            this.line_max_qty = this.props.line.qty
            this.state = useState({ productQty : this.props.line.qty });
            this.props.line.return_qty = this.props.line.qty;
        }
        captureChange(event){
             if(event.target.value > this.line_max_qty){
                alert('Cannot exceed more than available quantity!!')
                this.state.productQty = this.line_max_qty;
                return
             }else{
                this.props.line.return_qty = this.state.productQty;
             }
        }
        clickMinus(){
            if(this.props.line.qty == 1){
                this.props.line.return_qty = this.props.line.qty;
                return
            }else{
                this.props.line.qty -= 1
                this.state.productQty = this.props.line.qty;
                this.props.line.return_qty = this.props.line.qty;
                return this.props.line.qty;
            }
        }
        clickPlus(){
            if(this.props.line.qty == this.line_max_qty){
                return;
            }else{
                this.props.line.qty += 1;
                this.state.productQty = this.props.line.qty;
                this.props.line.return_qty = this.props.line.qty;
                return this.props.line.qty;
            }
        }
    }

    PopupProductLines.template = 'PopupProductLines';

    Registries.Component.add(PopupProductLines);

    return PopupProductLines;
});
