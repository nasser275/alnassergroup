# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timezone
from datetime import datetime, timedelta, date
import calendar
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import pytz


class user(models.Model):
    _inherit = 'res.users'

    def test__1(self):
        pass


class AppOrder(models.Model):
    _name = 'app.order'
    _description = 'App Order'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(string='Name', copy=False, readonly=True, index=True, translate=True)
    origin = fields.Char(string='Reference', copy=False, readonly=True, index=True, translate=True)
    order_address = fields.Char(string='Order Address')
    call_center_agent_name = fields.Char(string='Call Center Agent Name')
    customer_notes = fields.Text(string="Customer Notes")
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, index=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id.id)
    branch_id = fields.Many2one('res.branch', string='Branch', required=True, index=True,
                                default=lambda self: self.env.user.branch_id.id)
    external_app_id = fields.Integer(string='App ID', copy=False)
    synced = fields.Boolean(string='Is Synced', copy=False, readonly=True)
    created_from_schedule = fields.Boolean(string='Created From Schedule', copy=False, readonly=True)
    deleted_synced = fields.Boolean(string='Is Deleted Synced', copy=False, readonly=True)
    deleted = fields.Boolean(string='Is Deleted', copy=False, track_visibility='onchange', readonly=True)
    sales_person = fields.Many2one('res.users', string='Sales Person', required=False)
    order_date = fields.Date(copy=False)
    pos_created_time = fields.Datetime(copy=False, required=False)
    customer_suggestion = fields.Text(string="Customer Suggestion")
    order_source_id = fields.Many2one(comodel_name="pos.order.source", string="Order Source", required=False)
    free_delivery = fields.Boolean(string="Free Delivery")
    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount Type')
    discount = fields.Float(string="Discount", required=False)
    discount_amount = fields.Float(string="Discount Amount", required=False, compute='_amount_all')
    cancel_reason = fields.Selection(string='Cancel Reason',
                                     selection=[
                                         ('Out of zone', 'Out of zone'),
                                         ('Delivery Delay', 'Delivery Delay'),
                                         ('Out Of Stock', 'Out Of Stock'),
                                         ('Duplicated Order', 'Duplicated Order'),
                                         ('Scheduled', 'Scheduled'),
                                         ('High price', 'High price'),
                                         ('High Shipping', 'High Shipping'),
                                     ])
    return_reason = fields.Selection(string='Return Reason',
                                     selection=[
                                         ('Product quality', 'Product quality'),
                                         ('Order not complete', 'Order not complete'),
                                         ('Expired', 'Expired'),
                                         ('Bad taste', 'Bad taste'),
                                         ('Wrong products', 'Wrong products'),
                                         ('Other', 'Other'),
                                     ])

    delivery_cost = fields.Float(string="Delivery Cost")
    pos_delivered_time = fields.Datetime(copy=False, required=False)
    # Start schedule part
    week_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    is_schedule = fields.Boolean(string="Is Schedule")
    saturday = fields.Boolean(string="Saturday")
    sunday = fields.Boolean(string="Sunday")
    monday = fields.Boolean(string="Monday")
    tuesday = fields.Boolean(string="Tuesday")
    wednesday = fields.Boolean(string="Wednesday")
    thursday = fields.Boolean(string="Thursday")
    friday = fields.Boolean(string="Friday")
    schedule_start_date = fields.Date(copy=False, required=False)
    schedule_end_date = fields.Date(copy=False, required=False)
    due_date = fields.Datetime(copy=False, required=False)
    schedule_time = fields.Selection([
        ('0', '00'), ('1', '1:00'), ('2', '2:00'), ('3', '3:00'), ('4', '4:00'), ('5', '5:00'), ('6', '6:00'),
        ('7', '7:00'),
        ('8', '8:00'), ('9', '9:00'), ('10', '10:00'), ('11', '11:00'), ('12', '12:00'), ('13', '13:00'),
        ('14', '14:00'),
        ('15', '15:00'), ('16', '16:00'), ('17', '17:00'), ('18', '18:00'), ('19', '19:00'), ('20', '20:00'),
        ('21', '21:00'),
        ('22', '22:00'), ('23', '23:00'), ('24', '24:00'),
    ], string='Schedule Time', default="0", copy=False)
    saturday_time = fields.Selection([
        ('0', '00'), ('1', '1:00'), ('2', '2:00'), ('3', '3:00'), ('4', '4:00'), ('5', '5:00'), ('6', '6:00'),
        ('7', '7:00'),
        ('8', '8:00'), ('9', '9:00'), ('10', '10:00'), ('11', '11:00'), ('12', '12:00'), ('13', '13:00'),
        ('14', '14:00'),
        ('15', '15:00'), ('16', '16:00'), ('17', '17:00'), ('18', '18:00'), ('19', '19:00'), ('20', '20:00'),
        ('21', '21:00'),
        ('22', '22:00'), ('23', '23:00'), ('24', '24:00'),
    ], string='Saturday Time', default="0", copy=False)
    sunday_time = fields.Selection([
        ('0', '00'), ('1', '1:00'), ('2', '2:00'), ('3', '3:00'), ('4', '4:00'), ('5', '5:00'), ('6', '6:00'),
        ('7', '7:00'),
        ('8', '8:00'), ('9', '9:00'), ('10', '10:00'), ('11', '11:00'), ('12', '12:00'), ('13', '13:00'),
        ('14', '14:00'),
        ('15', '15:00'), ('16', '16:00'), ('17', '17:00'), ('18', '18:00'), ('19', '19:00'), ('20', '20:00'),
        ('21', '21:00'),
        ('22', '22:00'), ('23', '23:00'), ('24', '24:00'),
    ], string='Sunday Time', default="0", copy=False)
    monday_time = fields.Selection([
        ('0', '00'), ('1', '1:00'), ('2', '2:00'), ('3', '3:00'), ('4', '4:00'), ('5', '5:00'), ('6', '6:00'),
        ('7', '7:00'),
        ('8', '8:00'), ('9', '9:00'), ('10', '10:00'), ('11', '11:00'), ('12', '12:00'), ('13', '13:00'),
        ('14', '14:00'),
        ('15', '15:00'), ('16', '16:00'), ('17', '17:00'), ('18', '18:00'), ('19', '19:00'), ('20', '20:00'),
        ('21', '21:00'),
        ('22', '22:00'), ('23', '23:00'), ('24', '24:00'),
    ], string='Monday Time', default="0", copy=False)
    tuesday_time = fields.Selection([
        ('0', '00'), ('1', '1:00'), ('2', '2:00'), ('3', '3:00'), ('4', '4:00'), ('5', '5:00'), ('6', '6:00'),
        ('7', '7:00'),
        ('8', '8:00'), ('9', '9:00'), ('10', '10:00'), ('11', '11:00'), ('12', '12:00'), ('13', '13:00'),
        ('14', '14:00'),
        ('15', '15:00'), ('16', '16:00'), ('17', '17:00'), ('18', '18:00'), ('19', '19:00'), ('20', '20:00'),
        ('21', '21:00'),
        ('22', '22:00'), ('23', '23:00'), ('24', '24:00'),
    ], string='Tuesday Time', default="0", copy=False)
    wednesday_time = fields.Selection([
        ('0', '00'), ('1', '1:00'), ('2', '2:00'), ('3', '3:00'), ('4', '4:00'), ('5', '5:00'), ('6', '6:00'),
        ('7', '7:00'),
        ('8', '8:00'), ('9', '9:00'), ('10', '10:00'), ('11', '11:00'), ('12', '12:00'), ('13', '13:00'),
        ('14', '14:00'),
        ('15', '15:00'), ('16', '16:00'), ('17', '17:00'), ('18', '18:00'), ('19', '19:00'), ('20', '20:00'),
        ('21', '21:00'),
        ('22', '22:00'), ('23', '23:00'), ('24', '24:00'),
    ], string='Wednesday Time', default="0", copy=False)
    thursday_time = fields.Selection([
        ('0', '00'), ('1', '1:00'), ('2', '2:00'), ('3', '3:00'), ('4', '4:00'), ('5', '5:00'), ('6', '6:00'),
        ('7', '7:00'),
        ('8', '8:00'), ('9', '9:00'), ('10', '10:00'), ('11', '11:00'), ('12', '12:00'), ('13', '13:00'),
        ('14', '14:00'),
        ('15', '15:00'), ('16', '16:00'), ('17', '17:00'), ('18', '18:00'), ('19', '19:00'), ('20', '20:00'),
        ('21', '21:00'),
        ('22', '22:00'), ('23', '23:00'), ('24', '24:00'),
    ], string='Thursday Time', default="0", copy=False)
    friday_time = fields.Selection([
        ('0', '00'), ('1', '1:00'), ('2', '2:00'), ('3', '3:00'), ('4', '4:00'), ('5', '5:00'), ('6', '6:00'),
        ('7', '7:00'),
        ('8', '8:00'), ('9', '9:00'), ('10', '10:00'), ('11', '11:00'), ('12', '12:00'), ('13', '13:00'),
        ('14', '14:00'),
        ('15', '15:00'), ('16', '16:00'), ('17', '17:00'), ('18', '18:00'), ('19', '19:00'), ('20', '20:00'),
        ('21', '21:00'),
        ('22', '22:00'), ('23', '23:00'), ('24', '24:00'),
    ], string='Friday Time', default="0", copy=False)
    #  End schedule part
    state = fields.Selection([
        ('draft', 'Draft'),
        ('received', 'Received'),
        ('delivery', 'Delivery'),
        ('payment', 'Payment'),
        ('cancel', 'Cancelled'),
        ('return', 'Returned'),
    ], string='Status', default="draft", readonly=True, track_visibility='onchange', copy=False)
    app_lines = fields.One2many(comodel_name='app.order.lines', inverse_name='app_order_id', string='App Lines',
                                required=False)
    amount_total = fields.Float(string='Total', store=True, readonly=True, compute='_amount_all')
    final_total = fields.Float(string='Final Total', store=True, readonly=True, compute='_amount_all')
    order_platform = fields.Char(string='Order Platform')
    is_paid = fields.Boolean(string='Payment', default=False)
    sync = fields.Boolean(copy=False)

    @api.model
    def sync_app_order_to_pos(self, branch_id=False):
        print('HHHHH')
        if branch_id:
            domain = [('state', 'not in', ['cancel', 'return']),
                      ('branch_id', 'in', branch_id),
                      ('synced', '=', False), ('created_from_schedule', '=', False),
                      ('order_date', '=', fields.Date.today())]
        else:
            domain = [('state', 'not in', ['cancel', 'return']), ('synced', '=', False),
                      ('created_from_schedule', '=', False), ('order_date', '=', fields.Date.today())]
        not_synced_read = self.search_read(domain, fields=[
            'name', 'partner_id', 'branch_id', 'external_app_id', 'sales_person', 'order_date',
            'state', 'amount_total', 'app_lines', 'create_date', 'delivery_cost', 'schedule_time',
            'order_platform', 'order_address', 'customer_suggestion', 'customer_notes', 'free_delivery',
            'discount_type', 'discount', 'discount_amount', 'final_total'
        ])
        print(not_synced_read)
        not_synced_lines_read = []
        for order in not_synced_read:
            record = self.search([('id', '=', order['id'])])
            not_synced_lines_read.append(
                self.env['app.order.lines'].search_read([('app_order_id', '=', order['id'])], fields=[
                    'product_id', 'qty', 'price', 'subtotal', 'app_order_id', 'discount',
                ]))
            record.update({'synced': True})
        print('not_synced_read', not_synced_read)
        print('not_synced_read_line', not_synced_lines_read)
        return {'not_synced_read': not_synced_read, 'not_synced_lines_read': not_synced_lines_read}

    @api.model
    def sync_deleted_app_order_to_pos(self, branch_id=False):
        if branch_id:
            domain = [('state', 'not in', ['cancel', 'return']), ('branch_id', 'in', branch_id),
                      ('deleted', '=', True), ('deleted_synced', '=', False)]
        else:
            domain = [('state', 'not in', ['cancel', 'return']), ('deleted', '=', True), ('deleted_synced', '=', False)]
        deleted_not_synced_read = self.search(domain)
        # print('deleted_not_synced_read', send_messagedeleted_not_synced_read)
        deleted_not_synced_lines_read = []
        for order in deleted_not_synced_read:
            record = self.search([('id', '=', order.id)])
            deleted_not_synced_lines_read += self.env['app.order.lines'].search(
                [('app_order_id', '=', order['id'])]).ids
            record.update({'deleted_synced': True})
        print('deleted_not_synced_read,deleted_not_synced_lines_read', deleted_not_synced_read,
              deleted_not_synced_lines_read)
        return {'deleted_not_synced_read': deleted_not_synced_read.ids,
                'deleted_not_synced_lines_read': deleted_not_synced_lines_read}
        # return deleted_not_synced_read.ids

    @api.depends('app_lines.subtotal', 'discount_type', 'discount')
    def _amount_all(self):
        for order in self:
            amount_total = 0.0
            discount_amount = 0.0
            for line in order.app_lines:
                amount_total += line.subtotal
            if order.discount_type == 'percent' and order.discount:
                discount_amount = amount_total * (order.discount / 100)
            if order.discount_type == 'amount' and order.discount:
                discount_amount = order.discount
            order.update({
                'amount_total': amount_total,
                'final_total': amount_total - discount_amount,
                'discount_amount': discount_amount
            })

    @api.model
    def action_add_schedule_from_pos(self, order_id, data):
        print('mark_app_order_as_schedule =====> order_id,data', order_id, data)
        # schedule_start_date_utc_time, schedule_end_date_utc_time = self._convert_string_to_uct_datetime(data)
        app_order = self.search([('id', '=', order_id)])
        app_order.write({
            'is_schedule': data.get('is_schedule'),
            'saturday': True if data.get('saturday') == 'true' else False,
            'sunday': True if data.get('sunday') == 'true' else False,
            'monday': True if data.get('monday') == 'true' else False,
            'tuesday': True if data.get('tuesday') == 'true' else False,
            'wednesday': True if data.get('wednesday') == 'true' else False,
            'thursday': True if data.get('thursday') == 'true' else False,
            'friday': True if data.get('friday') == 'true' else False,
            'schedule_start_date': data.get('schedule_start_date'),
            'schedule_end_date': data.get('schedule_end_date'),
        })
        return True

    def _convert_string_to_uct_datetime(self, data):
        schedule_start_date_time_obj = datetime.strptime(data.get('schedule_start_date'), '%Y-%m-%d %H:%M:%S')
        schedule_start_date_utc_time = schedule_start_date_time_obj.replace(tzinfo=timezone.utc)
        schedule_end_date_time_obj = datetime.strptime(data.get('schedule_end_date'), '%Y-%m-%d %H:%M:%S')
        schedule_end_date_utc_time = schedule_end_date_time_obj.replace(tzinfo=timezone.utc)
        return schedule_start_date_utc_time, schedule_end_date_utc_time

    def convert_TZ_UTC(self, TZ_datetime):
        tz = "Africa/Cairo"
        try:
            tz = pytz.timezone(tz)
        except Exception:
            tz = False
        tz = tz or pytz.utc
        utc_timezone = pytz.utc.localize(datetime.strptime(TZ_datetime, "%Y-%m-%d %H:%M:%S")).astimezone(tz)
        return utc_timezone

    def _compute_due_date(self, date, hour):
        due_date_str = "{} {}:{}:{}".format(date, hour, 0, 0)
        due_date_time = datetime.strptime(due_date_str, '%Y-%m-%d %H:%M:%S') - timedelta(hours=2)
        return due_date_time

    @api.model
    def action_create_app_order_from_pos(self, data):
        print('action_create_app_order_from_pos =====> data', data)
        lines = []
        for line in data.get('app_lines'):
            lines.append((0, 0,
                          {'product_id': line.get('product_id'), 'qty': line.get('qty'), 'price': line.get('price'),
                           'discount': line.get('discount')}))
        all_data = {
            'is_schedule': data.get('is_schedule'),
            'saturday': True if data.get('saturday') == 'true' else False,
            'sunday': True if data.get('sunday') == 'true' else False,
            'monday': True if data.get('monday') == 'true' else False,
            'tuesday': True if data.get('tuesday') == 'true' else False,
            'wednesday': True if data.get('wednesday') == 'true' else False,
            'thursday': True if data.get('thursday') == 'true' else False,
            'friday': True if data.get('friday') == 'true' else False,
            'schedule_start_date': data.get('schedule_start_date'),
            'schedule_end_date': data.get('schedule_end_date'),
            'origin': data.get('origin'),
            'sales_person': data.get('sales_person'),
            # 'company_id': data.get('company_id'),
            'branch_id': data.get('branch_id'),
            'partner_id': data.get('partner_id'),
            'order_date': fields.Date.today(),
            'saturday_time': data.get('saturday_time'),
            'sunday_time': data.get('sunday_time'),
            'monday_time': data.get('monday_time'),
            'tuesday_time': data.get('tuesday_time'),
            'wednesday_time': data.get('wednesday_time'),
            'thursday_time': data.get('thursday_time'),
            'friday_time': data.get('friday_time'),
            'created_from_schedule': data.get('created_from_schedule'),
            'app_lines': lines
        }
        print('all_data ==========>', all_data)
        new_order = self.env['app.order'].sudo().create(all_data)
        if new_order:
            all_data['order_id'] = new_order.id
            print('all_data ==========>  after created ', all_data)
            self.create_app_orders_work_for_schedule(all_data)
            return True
        else:
            return False

    @api.model
    def action_create_app_order_from_cron(self, order_id, order_date, schedule_time):
        print('order_id,order_date, schedule_time', order_id, order_date, schedule_time)
        app_order = self.search([('id', '=', order_id)])
        due_date = self._compute_due_date(order_date, int(schedule_time))
        lines = []
        for line in app_order.app_lines:
            lines.append((0, 0, {'product_id': line.product_id.id, 'qty': line.qty, 'price': line.price,
                                 'discount': line.discount}))
        all_data = {
            'origin': app_order.name,
            'sales_person': app_order.sales_person.id,
            'partner_id': app_order.partner_id.id,
            # 'company_id': app_order.company_id.id,
            'branch_id': app_order.branch_id.id,
            'order_date': order_date,
            'schedule_time': schedule_time,
            'due_date': due_date,
            'app_lines': lines
        }
        print('cron created =-------', all_data)
        new_order = self.sudo().create(all_data)
        if new_order:
            return True
        else:
            return False

    def _convert_string_to_date(self, date):
        due_date_time = datetime.strptime(date, '%Y-%m-%d')
        return due_date_time.date()

    def create_app_orders_work_for_schedule(self, schedule_data):
        start = self._convert_string_to_date(schedule_data.get('schedule_start_date'))
        end = self._convert_string_to_date(schedule_data.get('schedule_end_date'))
        date_list = self.date_range(start, end)
        week_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for sc_date in date_list:
            for day in week_days:
                if any([schedule_data.get(day) for day in week_days]):
                    # if sc_date == fields.Date.today():
                    if schedule_data.get(day):
                        week_index = sc_date.weekday()
                        weekday_string_from_list = week_days[week_index]
                        if weekday_string_from_list == day:
                            self.action_create_app_order_from_cron(schedule_data.get('order_id'), sc_date,
                                                                   schedule_data.get(day + '_time'))

    def getLastDayInTheMonth(self):
        date_today = fields.Date.today()
        month = date_today.month
        day_number = calendar.monthrange(date_today.year, month)
        return day_number[1]

    def date_range(self, date_from, date_to):
        lst_date_range = []
        delta = date_to - date_from
        for i in range(abs(delta.days) + 1):
            day = date_from + timedelta(days=i)
            lst_date_range.append(day)
        return lst_date_range

    def action_received(self):
        self.state = 'received'

    def action_delivery(self):
        self.state = 'delivery'

    def action_payment(self):
        self.state = 'payment'

    def action_cancelled(self):
        if not self.cancel_reason:
            raise ValidationError(_('Please select a Cancel reason first.'))
        else:
            self.state = 'cancel'

    def action_returned(self):
        if not self.return_reason:
            raise ValidationError(_('Please select a return reason first.'))
        else:
            self.state = 'return'

    @api.model
    def action_change_state_from_pos(self, order_id, state, sales_person_id):
        print('order_id', order_id, state)
        order = self.search([('id', 'in', [order_id])])
        if state == 'received' and sales_person_id:
            order.write({'sales_person': sales_person_id})
        order.write({'state': state})
        # ================== #
        if state == 'delivery':
            # print('delivery =======================> 1')
            if not order.pos_created_time:
                # print('=======================> 2', fields.Datetime.now())
                order.pos_created_time = fields.Datetime.now()
        if state == 'payment':
            # print('payment =======================> 3')
            if not order.pos_created_time and not order.pos_delivered_time:
                # print('payment =======================> 4')
                order.pos_created_time = fields.Datetime.now()
                order.pos_delivered_time = fields.Datetime.now()
            elif order.pos_created_time and not order.pos_delivered_time:
                # print('payment =======================> 5')
                order.pos_delivered_time = fields.Datetime.now()
        # =========================== #
        # http requester part
        if state in ['delivery', 'payment']:
            self._send_user_verify_on_state_payment_and_delivery(order)
        return order.id

    @api.model
    def new_app_order_count(self):
        order_count = self.search_count(
            [('state', '=', 'draft'), ('order_date', '=', fields.Date.today()), ('deleted', '=', False),
             ('synced', '=', False), ('created_from_schedule', '=', False)])
        return order_count

    @api.model
    def app_order_count(self):
        order_count = self.search_count(
            [('state', '=', 'draft'), ('order_date', '=', fields.Date.today()), ('deleted', '=', False),
             ('created_from_schedule', '=', False)])
        return order_count

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('app.order')

        self.sync_app_order_to_pos()
        self.sync_deleted_app_order_to_pos()
        # self.action_add_schedule_from_pos()

        res = super(AppOrder, self).create(vals)
        # if not self.order_source and self.partner_id.how_know_us:
        #     self.order_source = self.partner_id.how_know_us
        # if not self.partner_id.how_know_us and self.order_source:
        #     self.partner_id.how_know_us = self.order_source

        return res

    def unlink(self):
        for record in self:
            record.deleted = True
        return True


class AppOrderLines(models.Model):
    _name = 'app.order.lines'

    app_order_id = fields.Many2one('app.order', string='App Order ID', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    qty = fields.Float(string='Qty', default=1, required=True)
    price = fields.Float(string='Price', default=1, required=True)
    discount = fields.Float(string='Discount %')
    subtotal = fields.Float(string='Subtotal', compute="_compute_qty_price", store=True, index=True)

    def read_converted(self):
        field_names = ["product_id", "price", "qty", "discount"]
        results = []
        for sale_line in self:
            item = sale_line.read(field_names)[0]
            results.append(item)
        return results

    @api.depends('qty', 'price', 'discount')
    def _compute_qty_price(self):
        for line in self:
            if line.qty and line.price:
                line.subtotal = (line.qty * line.price) * (1 - (line.discount or 0.0) / 100.0)


class POSOrder(models.Model):
    _inherit = 'pos.order'

    app_order_id = fields.Many2one('app.order', string='APP Order', readonly=True)
    call_center_agent_name = fields.Char(string='Call Center Agent Name', related='app_order_id.call_center_agent_name',
                                         store=True)

    def _order_fields(self, ui_order):
        order = super(POSOrder, self)._order_fields(ui_order)
        order['app_order_id'] = ui_order.get('app_order_id')
        print('D>D>D>SSSSSSSSSSSSSSSSSS', ui_order, order['app_order_id'])
        if ui_order.get('app_order_id'):
            app_order_id = self.env['app.order'].browse(ui_order.get('app_order_id'))
            order['call_center_agent_name'] = app_order_id.call_center_agent_name
            order['order_source_id'] = app_order_id.order_source_id.id
            app_order_id.sudo().write({'state': 'received'})
        return order

    def write(self, values):
        res = super(POSOrder, self).write(values)
        for order in self:
            if order.state == 'paid':
                app_order_id = self.env['app.order'].browse(order.app_order_id.id)
                app_order_id.sudo().write({'state': 'payment'})
        return res


class PosOrderReport(models.Model):
    _inherit = "report.pos.order"
    call_center_agent_name = fields.Char(string='Call Center Agent Name')
    customer_name_phone = fields.Char(string="Customer Name & Phone", required=False)

    def _from(self):
        return """
               FROM pos_order_line AS l
                   INNER JOIN pos_order s ON (s.id=l.order_id)
                   LEFT JOIN product_product p ON (l.product_id=p.id)
                   LEFT JOIN product_template pt ON (p.product_tmpl_id=pt.id)
                   LEFT JOIN uom_uom u ON (u.id=pt.uom_id)
                   LEFT JOIN pos_session ps ON (s.session_id=ps.id)
                   LEFT JOIN res_company co ON (s.company_id=co.id)
                   LEFT JOIN res_currency cu ON (co.currency_id=cu.id)
                   LEFT JOIN res_partner part ON (s.partner_id=part.id)
           """

    def _select(self):
        return super(PosOrderReport,
                     self)._select() + ',s.call_center_agent_name AS call_center_agent_name,concat(part.name, part.phone) as customer_name_phone'

    def _group_by(self):
        return super(PosOrderReport, self)._group_by() + ',s.call_center_agent_name,concat(part.name, part.phone)'
