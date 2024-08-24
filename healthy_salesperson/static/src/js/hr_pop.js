odoo.define('healthy_salesperson.hr_pop', function (require) {
    "use strict";


    var rpc = require('web.rpc');
    var _t = require('web.core')._t;
    const Registries = require('point_of_sale.Registries');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const {Gui} = require('point_of_sale.Gui');
    const ajax = require('web.ajax');

    const {
        useState,
        useRef
    } = owl.hooks;


    class POSSalesPersonPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);

            this.state = useState({
                sales_person: this.props.sales_person,
                salespersons: this.env.pos.salespersons,
            })


        }


        getPayload() {
            var selected_vals = [];
            var sales_person = this.state.sales_person;
            selected_vals.push(sales_person);
            return selected_vals
        }

        mounted() {


        }


        click_confirm() {
            var self = this;
            var payload = this.getPayload();
            var order = this.env.pos.get_order();
            order.sales_person = payload[0];
            self.trigger('close-popup');


        }
              async updateSalespersons(event) {
            var list1 = [];
            if (event.target.value) {

                for (const item of this.state.salespersons) {
                    if (item.name.includes(event.target.value)) {
                        list1.push(item)
                    }
                }
                this.state.salespersons = list1
                this.render();
            } else {

                this.state.salespersons = this.env.pos.salespersons
                this.render();
            }

        }



    }

    POSSalesPersonPopup.template = 'POSSalesPersonPopup';
    POSSalesPersonPopup.defaultProps = {
        confirmText: 'Select',
        cancelText: 'Cancel',
        title: 'Set Sales Represtiative',
        body: '',
    };

    Registries.Component.add(POSSalesPersonPopup);
    return POSSalesPersonPopup;


});