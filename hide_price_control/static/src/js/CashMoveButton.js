odoo.define('hide_price_control.cashinout', function (require) {
    "use strict";

    const CashMoveButton = require('point_of_sale.CashMoveButton');
    const Registries = require('point_of_sale.Registries');
    const { _t } = require('web.core');
    const TRANSLATED_CASH_MOVE_TYPE = {
        in: _t('in'),
        out: _t('out'),
    };
        const { Component } = owl;

    const CustomCashMoveButton = CashMoveButton =>
        class extends CashMoveButton {
        async  askPin(pin) {
            const { confirmed, payload: inputPin } = await this.showPopup('NumberPopup', {
                isPassword: true,
                title: this.env._t('Password ?'),
                startingValue: null,
            });

            if (!confirmed) return false;
            console.log("pin",pin,inputPin)
            if (pin === inputPin) {
                return true;
            } else {
                await this.showPopup('ErrorPopup', {
                    title: this.env._t('Incorrect Password'),
                });
                return false;
            }
        }

            async onClick() {
                const employee = this.env.pos.get_cashier();
                if (employee.use_pos_password) {
                    var result=await this.askPin(employee.user_password);
                    if (result){
                        this.open_cash()
                    }
                } else {
                    return this.showPopup('ErrorPopup', {
                            title: ('Unknown User'),
                            body: ("Not Allow!"),
                        });
                    // this.open_cash()
                }

        }

            async open_cash() {
                const current = Component.current;
                const {confirmed, payload} = await this.showPopup('CashMovePopup');
                if (!confirmed) return;
                const {type, amount, reason} = payload;
                const translatedType = TRANSLATED_CASH_MOVE_TYPE[type];
                const formattedAmount = this.env.pos.format_currency(amount);
                if (!amount) {
                    return this.showNotification(
                        _.str.sprintf(this.env._t('Cash in/out of %s is ignored.'), formattedAmount),
                        3000
                    );
                }
                const extras = {formattedAmount, translatedType};
                await this.rpc({
                    model: 'pos.session',
                    method: 'try_cash_in_out',
                    args: [[this.env.pos.pos_session.id], type, amount, reason, extras],
                });
                if (this.env.pos.proxy.printer) {
                    const renderedReceipt = this.env.qweb.renderToString('point_of_sale.CashMoveReceipt', {
                        _receipt: this._getReceiptInfo({...payload, translatedType, formattedAmount}),
                    });
                    const printResult = await this.env.pos.proxy.printer.print_receipt(renderedReceipt);
                    if (!printResult.successful) {
                        this.showPopup('ErrorPopup', {
                            title: printResult.message.title,
                            body: printResult.message.body
                        });
                    }
                }
                this.showNotification(
                    _.str.sprintf(this.env._t('Successfully made a cash %s of %s.'), type, formattedAmount),
                    3000
                );
            }

        };

    Registries.Component.extend(CashMoveButton, CustomCashMoveButton);

    return CashMoveButton;






});
