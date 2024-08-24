odoo.define('point_of_sale.CreateSaleOrderScreen', function(require) {
    'use strict';

    const IndependentToOrderScreen = require('point_of_sale.IndependentToOrderScreen');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useState, useRef } = owl.hooks;
    const { useListener } = require('web.custom_hooks');
    var rpc = require('web.rpc');

    class CreateSaleOrderScreen extends IndependentToOrderScreen {
        constructor(){
            super(...arguments);
            useListener('update-signature-fields', this._updateSignatureFields);
            this.state = useState({ activeTab: 'ShippingAddress',orderNote:'',gstTreatment: '',ShipToDifferentAdd : false,
                                    InvToDifferentAdd: false,shippingContact :[],invoiceContact :[],
                                    selectedShippingContact:'',selectedInvoiceContact:'',SignedBy : '',
                                    SignedOn :moment().format('YYYY-MM-DD'),orderDate : moment().format('YYYY-MM-DD'),
                                    requestedDate:moment().format('YYYY-MM-DD'),S_client_name : '',S_client_email:'',
                                    S_client_city:'',S_client_zip:'',S_client_mobile:'',S_client_phone:'',
                                    invoiceData:{name:'', street:'', city:'', zip: '', phone: '',
                                                email: '',mobile: ''},currentInput:false});
            this._getClientDetails();
            this._isEditQuotation();
        }
        captureCountryChange(input){
            console.log('input.target.autocomplete',document.querySelector())
        }
        captureChange(event){
            this.state.invoiceData[event.target.name] = event.target.value;
        }
        validateEmail(value){
            var emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
            return emailPattern.test(value);
        }
        onInputKeyDown(e){
            if(e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57) && (e.which < 96 || e.which > 105)) {
                e.preventDefault();
            }
        }
        async _getClientDetails(){
            let partner = this.env.pos.get_order().get_client();
            var params = {
                model: 'res.partner',
                method: 'search_read',
                domain: [['parent_id', '=', partner.id]]
            }
            var contacts = await this.rpc(params);
            let shippingPartners = contacts.filter((record) => record.type === 'delivery');
            let invoicePartners = contacts.filter((record) => record.type === 'invoice');
            this.state.shippingContact = shippingPartners;
            this.state.invoiceContact = invoicePartners;
        }
        async _isEditQuotation(){
            if(this.env.pos.get_order().get_is_quotation()){
                let sale_order_id = this.env.pos.get_order().get_sale_order_id_to_edit();
                let sale_order = this.env.pos.db.get_order_by_id(sale_order_id);
                this.state.orderNote = sale_order.note ? sale_order.note : '';
                // this.state.gstTreatment = sale_order.l10n_in_gst_treatment ? sale_order.l10n_in_gst_treatment : '';
                this.state.orderDate = sale_order.date_order ?  moment(sale_order.date_order).format('YYYY-MM-DD') : '';
                this.state.selectedShippingContact = sale_order.partner_shipping_id ? sale_order.partner_shipping_id : '';
                this.state.selectedInvoiceContact = sale_order.partner_invoice_id ? sale_order.partner_invoice_id : '';
            }
        }
        _updateSignatureFields(event){
            this.state.SignedBy = event.detail.SignedBy;
            this.state.SignedOn = event.detail.SignedOn;
        }
        onClickTab(tab){
            this.state.activeTab = tab;
        }
        async _createSaleOrder(){
            var order = this.env.pos.get_order();
            if(this.env.pos.company.country.code == 'IN' && this.state.gstTreatment == ''){
                alert('Please Select gstTreatment !!');
                return
            }
            if(this.props.operation == 'direct_pay'){
                var body_string = 'SO';
            }else{
                let operation = this.env.pos.user.sale_order_operations;
                var body_string = operation == 'confirm' ?  'SO' : 'Quotation';
            }
            const { confirmed } = await this.showPopup('ConfirmPopup', {
                title: this.env._t('Confirmation'),
                body: this.env._t(
                    "Are you sure you want to create" + '  ' + body_string + "?"
                ),
            });
            if(confirmed){
                let invoice_val = await this.invoice_contact(order);
                let shipping_val = await this.shipping_contact(order);
                if(invoice_val && invoice_val[1] && shipping_val && shipping_val[1]){
                    if(invoice_val[0] == 'invoice_contact'){
                        await this.create_partner(order,invoice_val);
                    }
                    if(shipping_val[0] == 'shipping_contact'){
                        await this.create_partner(order,shipping_val);
                    }
                    this.create_sale_order(order,body_string);
                }else if(invoice_val && shipping_val){
                    this.create_sale_order(order,body_string);
                }else{
                    return
                }
            }
        }
        async create_partner(order,vals){
             var params = {
                model: 'res.partner',
                method: 'create',
                args: [vals[1]],
             }
             let new_partner_id = await this.rpc(params);
             if(vals[0] == 'invoice_contact'){
                order.set_invoice_address(new_partner_id);
             }
             if(vals[0] == 'shipping_contact'){
                order.set_shipping_address(new_partner_id);
             }
        }
        async invoice_contact(order){
            var self = this;
            if(this.state.selectedInvoiceContact && !this.state.InvToDifferentAdd){
                order.set_invoice_address(this.state.selectedInvoiceContact);
                return true;
            }else if(self.state.InvToDifferentAdd){
                if(!self.validateEmail(self.state.invoiceData['email'])){
                    alert('Invalid Email!')
                    return false;
                }else if(self.state.invoiceData['name'] == ''){
                    alert('Please enter name of invoice partner!!')
                    return false;
                }else{
                    var inv_val = {
                        'name': self.state.invoiceData['name'],
                        'email': self.state.invoiceData['email'],
                        'city': self.state.invoiceData['city'],
                        'state_id': Number($('option[value="'+$('#invoice_state').val()+'"]').attr('id')),
                        'zip': self.state.invoiceData['zip'],
                        'country_id': Number($('option[value="'+$('#invoice_country').val()+'"]').attr('id')),
                        'mobile': self.state.invoiceData['mobile'],
                        'phone': self.state.invoiceData['phone'],
                        'parent_id': order.get_client().id,
                        'type': 'invoice'
                    }
                    return ['invoice_contact',inv_val];
                }
            }else{
                return true;
            }
        }
        async shipping_contact(order){
            var self = this;
            if(this.state.selectedShippingContact && !this.state.ShipToDifferentAdd){
                order.set_shipping_address(this.state.selectedShippingContact);
                return true;
            }else if(this.state.ShipToDifferentAdd){
                if(!self.validateEmail(self.state.S_client_email)){
                    alert('Invalid Email!')
                    return false;
                }else if(self.state.S_client_name == ''){
                    alert('Please enter name of shipping partner!!')
                    return false;
                }else{
                    var ship_val = {
                        'name': self.state.S_client_name,
                        'email': self.state.S_client_email,
                        'city': self.state.S_client_city,
                        'state_id': Number($('option[value="'+$('#shipping_state').val()+'"]').attr('id')),
                        'zip': self.state.S_client_zip,
                        'country_id': Number($('option[value="'+$('#shipping_country').val()+'"]').attr('id')),
                        'mobile':self.state.S_client_mobile,
                        'phone': self.state.S_client_phone,
                        'parent_id': order.get_client().id,
                        'type': 'delivery'
                    }
                    return ['shipping_contact',ship_val];
                }
            }else{
                return true;
            }
        }
        async create_sale_order(order,body_string){
            var self = this;
            var currentOrderLines = order.get_orderlines();
            var customer_id = order.get_client().id;
            var location_id = this.env.pos.config.picking_type_id ? this.env.pos.config.picking_type_id[0] : false;
            var orderLines = [];
            for(var i=0; i<currentOrderLines.length;i++){
                orderLines.push(currentOrderLines[i].export_as_JSON());
            }
            if(this.props.operation == 'direct_pay'){
                var paymentLines = [];
                _.each(order.get_paymentlines(), function(paymentline){
                    paymentLines.push({
                        'journal_id': paymentline.payment_method['id'],
                        'amount': paymentline.get_amount(),
                    })
                });
            }
            var vals = {
                orderlines: orderLines,
                customer_id: customer_id,
                orderDate : this.state.orderDate,
                gstTreatment : this.state.gstTreatment,
                signed_by : this.state.SignedBy,
                signed_on : this.state.SignedOn,
                requestedDate: this.state.requestedDate,
                location_id: location_id,
                journal : paymentLines,
                operation: this.props.operation ? this.props.operation : self.env.pos.user.sale_order_operations,
                edit_quotation : order.get_is_quotation(),
                sale_order_id : order.get_sale_order_id(),
                partner_shipping_id: order.get_shipping_address() || customer_id,
                partner_invoice_id: order.get_invoice_address() || customer_id,
                sign : order.get_sign() ? order.get_sign() : false,
                note : this.state.orderNote ? this.state.orderNote : false,
            }
            var params = {
                model: 'sale.order',
                method: 'create_sales_order',
                args: [vals],
            }
            var new_orders = await rpc.query(params).then(function(order){
                if(order){
                    var exist_order = _.findWhere(self.env.pos.db.get_orders_list(), {'id': order[0].id})
                    if(exist_order){
                        _.extend(exist_order,order[0]);
                    }else{
                        self.env.pos.db.orders_list.push(order[0]);
                    }
                    var sorted_orders = _.sortBy(self.env.pos.db.get_orders_list(), 'id').reverse();
                    self.env.pos.db.add_orders(sorted_orders);
                    var url = window.location.origin + '/web#id=' + order[0].id + '&view_type=form&model=sale.order';
                    if(order[1]){
                        var exist_invoice = _.findWhere(self.env.pos.db.get_invoices_list(), {'id': order[1].id})
                        if(exist_invoice){
                            _.extend(exist_invoice,order[1]);
                        }else{
                            self.env.pos.db.invoices_list.push(order[1]);
                        }
                        self.env.pos.db.add_invoices(self.env.pos.db.get_invoices_list());
                    }
                    return {'url' : url, 'name': order[0].name,'id': order[0].id}
                }
            });
            const { confirmed } = await this.showPopup('SaleOrderConfirmPopup', {
                url : new_orders.url,
                name : new_orders.name,
                body : body_string,
            });
            if(confirmed){
                try{
                    await this.env.pos.do_action('sale.action_report_saleorder', {
                        additional_context: {
                            active_ids: [new_orders.id],
                        },
                    });
                }catch (error){
                    if (error instanceof Error) {
                        throw error;
                    }else {
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Network Error'),
                            body: this.env._t('Unable to download invoice.'),
                        });
                    }
                }
//                order.destroy()
//                this.showScreen('ProductScreen')
            }
//            else{
                order.destroy()
                this.showScreen('ProductScreen')
//            }
        }
        _closeScreen(){
            this.close();
        }
    }
    CreateSaleOrderScreen.template = 'CreateSaleOrderScreen';

    Registries.Component.add(CreateSaleOrderScreen);

    return CreateSaleOrderScreen;
});
