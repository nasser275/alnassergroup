odoo.define('healthy_order_source_discount.schedule_app_orders_pop', function (require) {
    "use strict";


    var rpc = require('web.rpc');
    var _t = require('web.core')._t;
    const Registries = require('point_of_sale.Registries');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');

    const {
        useState,
        useRef
    } = owl.hooks;


    class ScheduleAppOrderPopupWidget extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
        }

        mounted() {
            this.show()
        }

        show() {
            var self = this;
            $('.schedule-start-date').on('change', function (e) {
                console.log("$(this).val()", $(this).val());
            });
            $(".weekdays").on('change', function () {
                if ($(this).is(':checked')) {
                    $(this).attr('value', true);
                    var id = $(this).attr('id');
                    console.log('checked ==============================================', id, '.' + id + '_time');
                    $('.' + id + '_time').css('display', 'block');
                } else {
                    $(this).attr('value', false);
                    var id = $(this).attr('id');
                    $('.' + id + '_time').css('display', 'none');
                }
                // $(this).text($(this).val());
            });
        }

        convert_pm_time_to_army_time(day_time) {
            var final_value = '24'
            var weekday_time = $(day_time + ' option').filter(':selected').val();
            var weekday_time_pm = $(day_time + ' .schedule_shift option').filter(':selected').val();
            if (weekday_time_pm === 'PM') {
                console.log('weekday_time', weekday_time)
                if (weekday_time == '12') {
                    final_value = weekday_time
                } else {
                    final_date = parseInt(weekday_time) + 12
                    final_value = final_date.toString()
                }
            } else {
                if (weekday_time == '12') {
                    final_value = '24'
                } else {
                    final_value = weekday_time
                }
            }
            console.log('final_value', final_value)
            return final_value
        }

        create_schedule_app_order(data) {
            this.rpc({
                model: 'app.order',
                method: 'action_create_app_order_from_pos',
                args: [data]
            });

        }

        validate_24_hour_for_time(day_time_value) {
            var returned_value = '0'
            if (day_time_value == '24') {
                returned_value = '0';
            } else {
                returned_value = day_time_value;
            }
            return returned_value;
        }

        async click_create() {
            var self = this;
            var order = this.env.pos.get_order();
            var order_lines = this.env.pos.get_order().get_orderlines();
            console.log("======================= service order By salem ", order);
            var saturday = $('input#saturday.weekdays').val();
            var sunday = $('input#sunday.weekdays').val();
            var monday = $('input#monday.weekdays').val();
            var tuesday = $('input#tuesday.weekdays').val();
            var wednesday = $('input#wednesday.weekdays').val();
            var thursday = $('input#thursday.weekdays').val();
            var friday = $('input#friday.weekdays').val();
            var saturday_time = self.convert_pm_time_to_army_time('.saturday_time');
            var sunday_time = self.convert_pm_time_to_army_time('.sunday_time');
            var monday_time = self.convert_pm_time_to_army_time('.monday_time');
            var tuesday_time = self.convert_pm_time_to_army_time('.tuesday_time');
            var wednesday_time = self.convert_pm_time_to_army_time('.wednesday_time');
            var thursday_time = self.convert_pm_time_to_army_time('.thursday_time');
            var friday_time = self.convert_pm_time_to_army_time('.friday_time');
            var schedule_start_date = $('.schedule-start-date').val() || false;
            var schedule_end_date = $('.schedule-end-date').val() || false;
            var today = new Date().toISOString().slice(0, 10);
            console.log("=======================  schedule_start_date, schedule_end_date, today", schedule_start_date, schedule_end_date);
            console.log('======= times', saturday_time, sunday_time, monday_time, tuesday_time, wednesday_time, thursday_time, friday_time);
            if (saturday != 'true' && sunday != 'true' && monday != 'true' && tuesday != 'true' && wednesday != 'true' && thursday != 'true' && friday != 'true') {
                self.gui.show_popup('error', {
                    'title': _t('Unknown Week Days'),
                    'body': _t('Please choose at last one day from weekdays.'),
                });
                return;
            } else if (!schedule_start_date) {
                self.gui.show_popup('error', {
                    'title': _t('Unknown Schedule Start Date'),
                    'body': _t('Please set Schedule Start Date first.'),
                });
                return;
            } else if (saturday == 'true' && parseInt(saturday_time) <= 0) {
                self.gui.show_popup('error', {
                    'title': _t('Unknown Saturday Time'),
                    'body': _t('Please choose Saturday Time.'),
                });
                return;
            } else if (sunday == 'true' && parseInt(sunday_time) <= 0) {
                self.gui.show_popup('error', {
                    'title': _t('Unknown Sunday Time'),
                    'body': _t('Please choose Sunday Time.'),
                });
                return;
            } else if (monday == 'true' && parseInt(monday_time) <= 0) {
                self.gui.show_popup('error', {
                    'title': _t('Unknown Monday Time'),
                    'body': _t('Please choose Monday Time.'),
                });
                return;
            } else if (tuesday == 'true' && parseInt(tuesday_time) <= 0) {
                self.gui.show_popup('error', {
                    'title': _t('Unknown Tuesday Time'),
                    'body': _t('Please choose Tuesday Time.'),
                });
                return;
            } else if (wednesday == 'true' && parseInt(wednesday_time) <= 0) {
                self.gui.show_popup('error', {
                    'title': _t('Unknown Wednesday Time'),
                    'body': _t('Please choose Wednesday Time.'),
                });
                return;
            } else if (thursday == 'true' && parseInt(thursday_time) <= 0) {
                self.gui.show_popup('error', {
                    'title': _t('Unknown Thursday Time'),
                    'body': _t('Please choose Thursday Time.'),
                });
                return;
            } else if (friday == 'true' && parseInt(friday_time) <= 0) {
                this.showPopup('ErrorPopup', {
                    'title': _t('Unknown Friday Time'),
                    'body': _t('Please choose Friday Time.'),
                });
                return;
            } else if (!schedule_end_date) {
                this.showPopup('ErrorPopup', {
                    'title': _t('Unknown Schedule End Date'),
                    'body': _t('Please set Schedule End Date first.'),
                });
                return;
            } else if (schedule_start_date > schedule_end_date) {
                this.showPopup('ErrorPopup', {
                    'title': _t('Date Validate'),
                    'body': _t('Please make sure the start date bigger than end date.'),
                });
                return;
            } else if (schedule_start_date < today) {
                return this.showPopup('ErrorPopup', {
                    'title': 'Date Validate',
                    'body': 'Please make sure the start date bigger than Today.',
                });
                return;
            } else if (schedule_end_date < today) {
                return this.showPopup('ErrorPopup', {
                    'title': 'Date Validate',
                    'body': 'Please make sure the end date bigger than Today.',
                });

                return;
            }
            console.log("order['app_order_id']", order['app_order_id']);
            var app_order_data = {};
            app_order_data['partner_id'] = order.changed.client['id'];
            app_order_data['is_schedule'] = true;
            app_order_data['created_from_schedule'] = true;
            app_order_data['origin'] = order.name;
            app_order_data['company_id'] = order.pos.company['id'];
            app_order_data['branch_id'] = order.pos.branch['id'];
            app_order_data['sales_person'] = order.pos.user['id'];
            app_order_data['saturday'] = saturday;
            app_order_data['sunday'] = sunday;
            app_order_data['monday'] = monday;
            app_order_data['tuesday'] = tuesday;
            app_order_data['wednesday'] = wednesday;
            app_order_data['thursday'] = thursday;
            app_order_data['friday'] = friday;
            app_order_data['saturday_time'] = self.validate_24_hour_for_time(saturday_time),
                app_order_data['sunday_time'] = self.validate_24_hour_for_time(sunday_time),
                app_order_data['monday_time'] = self.validate_24_hour_for_time(monday_time),
                app_order_data['tuesday_time'] = self.validate_24_hour_for_time(tuesday_time),
                app_order_data['wednesday_time'] = self.validate_24_hour_for_time(wednesday_time),
                app_order_data['thursday_time'] = self.validate_24_hour_for_time(thursday_time),
                app_order_data['friday_time'] = self.validate_24_hour_for_time(friday_time),
                app_order_data['schedule_start_date'] = schedule_start_date;
            app_order_data['schedule_end_date'] = schedule_end_date;
            app_order_data['app_lines'] = [];
            if (order_lines.length > 0) {
                order_lines.forEach(function (line) {
                    app_order_data['app_lines'].push({
                        'product_id': line.product['id'],
                        'price': line.price,
                        'qty': line.quantity,
                        'discount': line.discount,
                    });
                });
            }
            await  self.create_schedule_app_order(app_order_data);
            // this.env.pos.add_new_order();
            this.trigger('close-popup');
        }
    }

    ScheduleAppOrderPopupWidget.template = 'ScheduleAppOrderPopupWidget';
    ScheduleAppOrderPopupWidget.defaultProps = {
        confirmText: 'Select',
        cancelText: 'Cancel',
        title: 'Set Order Source',
        body: '',
    };
    Registries.Component.add(ScheduleAppOrderPopupWidget);
    return ScheduleAppOrderPopupWidget;


});