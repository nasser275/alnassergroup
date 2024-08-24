<odoo>
    <data>

        <!--        <record model="ir.ui.view" id="stock_picking_type_view_kanban">-->
        <!--            <field name="name">stock.picking.type.view.kanban</field>-->
        <!--            <field name="model">stock.picking.type</field>-->
        <!--            <field name="inherit_id" ref="stock.stock_picking_type_kanban"/>-->
        <!--            <field name="arch" type="xml">-->

        <!--                <xpath expr="//field[@name='color']" position="after">-->
        <!--                    <field name="pos_branch_allow" invisible="1"/>-->
        <!--                    <field name="is_allow" invisible="1"/>-->
        <!--                </xpath>-->
        <!--            </field>-->
        <!--        </record>-->
        <!--        <record id="stock.stock_picking_type_action" model="ir.actions.act_window">-->
        <!--            <field name="name">Inventory Overview</field>-->
        <!--            <field name="type">ir.actions.act_window</field>-->
        <!--            <field name="res_model">stock.picking.type</field>-->
        <!--            <field name="domain">[('is_allow', '=',1)]</field>-->
        <!--        </record>-->

         <record id="access_to_onhand_group_product_transfer" model="res.groups">
            <field name="name">On Hand Access-Transfer</field>
        </record>
        <record id="view_form_replenishment" model="ir.ui.view">
            <field name="name">replenishment_form_view</field>
            <field name="model">alfa.replanishment</field>
            <field name="arch" type="xml">
                <form string="Transfer Order" delete="false">
                    <sheet>
                        <header>
                            <field name="branch_available_to" invisible="1" required="1"/>
                            <field name="branch_available_from" invisible="1"/>
                            <!--                        <field name="user" invisible="1"/>-->
                            <field name="state" widget="statusbar"/>
                            <button string="Request" type="object" name="set_request"
                                    attrs="{'invisible': [('state', '!=', 'draft')]}"/>
                            <button string="Approve" type="object" name="set_approve"
                                    attrs="{'invisible': ['|',('state', '!=', 'request'),('branch_available_from','!=',True)]}"/>
                            <button string="Confirm" type="object" name="set_confirm"
                                    attrs="{'invisible': ['|',('state', '!=', 'approve'),('branch_available_to','!=',True)]}"/>
                            <button string="Cancel" type="object" name="set_cancel"
                                    attrs="{'invisible': [('state' , 'in', ['confirm','draft','approve'])]}"/>
                        </header>
                        <!--                    <sheet>-->
                        <group>
                            <group>
                                <field name="warehouse_from"
                                       attrs="{'readonly':[('state' , 'in', ['confirm','request','approve'])]}"
                                       options='{"no_open": True,"no_create": True, "no_create_edit":True}'/>
                            </group>
                            <group>
                                <field name="warehouse_to"
                                       attrs="{'readonly':[('state' , 'in', ['confirm','request','approve'])]}"
                                       options='{"no_open": True,"no_create": True, "no_create_edit":True}'/>
                            </group>
                            <field name="date_action" invisible="1"/>
                        </group>
                        <notebook>
                                 <page string="Products" name="products">
                                <field name="provided_products" widget="section_and_note_one2many" attrs="{'readonly':[('state' , 'in', ['confirm'])]}" options="{&quot;no_open&quot;: True,&quot;no_create&quot;: True, &quot;no_create_edit&quot;:True}">
                                    <tree editable="bottom" delete="1">
                                        <field name="state" invisible="1"/>
                                        <field name="product" attrs="{'readonly': [('state' , 'in', ['confirm','approve'])]}" options="{'no_create':True}"/>
                                        <field name="product_category"/>
                                        <field name="available_qty"  groups="alfa.access_to_onhand_group_product_transfer"  readonly="1"/>
                                        <field name="uom"/>
                                        <field name="requested_qty" attrs="{'readonly': [('state','=', 'approve')]}" sum="requested_qty"/>
                                        <field name="approved_qty" attrs="{'readonly': ['|',('state','=', 'approve'),('state','=', 'draft')]}" sum="approved_qty"/>
                                        <field name="confirmed_qty" attrs="{'readonly': ['|',('state','=', 'request'),('state','=', 'draft')]}" sum="confirmed_qty" readonly="1"/>
                                    </tree>
                                </field>
                            </page>
                            <page string="References">
                                <group>
                                    <field name="sequence_num" readonly="1"/>
                                    <field name="sequence_confirm" readonly="1"/>
                                    <field name="transfer_ref_approve" readonly="1"/>
                                    <field name="transfer_ref_confirm" readonly="1"/>
                                </group>
                            </page>
                        </notebook>

                    </sheet>
                    <div class="oe_chatter">
                    <field name="message_follower_ids" widget="mail_followers"/>
                    <field name="activity_ids" widget="mail_activity"/>
                    <field name="message_ids" widget="mail_thread"/>
                </div>
                </form>
            </field>
        </record>
        <record id="view_tree_Replenishment" model="ir.ui.view">
            <field name="name">replenishment_tree_view</field>
            <field name="model">alfa.replanishment</field>
            <field name="arch" type="xml">
                <tree delete="false">
                    <field name="sequence_num"/>
                    <field name="date_action"/>
                    <field name="warehouse_from"/>
                    <field name="warehouse_to"/>
                    <field name="state"/>
                    <field name="transfer_ref_approve" optional="hide"/>
                    <field name="transfer_ref_confirm" optional="hide"/>
                    <field name="sequence_confirm" optional="hide"/>
                    <!--                    <field name="requested_qty"/>-->
                    <!--                    <field name="approved_qty"/>-->
                    <!--                    <field name="confirmed_qty"/>-->
                </tree>

            </field>
        </record>

        <record id="alfa_replanishment_view_search" model="ir.ui.view">
            <field name="name">alfa.replanishment.view.search</field>
            <field name="model">alfa.replanishment</field>
            <field name="arch" type="xml">
                <search>
                    <filter name="date_action" string="Date" date="date_action"/>
                    <filter name="sequence_num" string="Ref"/>
                    <filter name="warehouse_from" string="From"/>
                    <filter name="warehouse_to" string="To"/>
                    <field name="date_action" string="Date"/>
                    <field name="sequence_num" string="Ref"/>
                    <field name="warehouse_from" string="From"/>
                    <field name="warehouse_to" string="To"/>
                </search>
            </field>
        </record>


        <record id="action_replenishment_session" model="ir.actions.act_window">
            <field name="name">Transfers</field>
            <field name="type">ir.actions.act_window</field>
            <field name="res_model">alfa.replanishment</field>
            <field name="view_mode">tree,form</field>
            <field name="domain"></field>
            <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">
                    Click to add a new Transfer Order.
                </p>
            </field>
        </record>

        <record id="user_transfer_view_form" model="ir.ui.view">
            <field name="name">alfa.replanishment.form.inherit</field>
            <field name="model">alfa.replanishment</field>
            <field name="inherit_id" ref="alfa.view_form_replenishment"/>
            <field name="groups_id" eval="[(6, 0, [ref('alfa.transfer_user') ])]"/>
            <field name="arch" type="xml">
                <field name="warehouse_from" position="attributes">
                    <attribute name="readonly">1</attribute>
                </field>
                <field name="warehouse_to" position="attributes">
                    <attribute name="readonly">1</attribute>
                </field>
            </field>
        </record>

        <record id="manager_transfer_view_form" model="ir.ui.view">
            <field name="name">alfa.replanishment.form.inherit</field>
            <field name="model">alfa.replanishment</field>
            <field name="inherit_id" ref="alfa.view_form_replenishment"/>
            <field name="groups_id" eval="[(6, 0, [ref('alfa.transfer_manager') ])]"/>
            <field name="arch" type="xml">
                <field name="warehouse_from" position="attributes">
                    <attribute name="readonly">0</attribute>
                </field>
                <field name="warehouse_to" position="attributes">
                    <attribute name="readonly">0</attribute>
                </field>
            </field>
        </record>


        <menuitem id="replenishment"
                  name="Transfer Between Warehouses"
                  action="action_replenishment_session"
                  sequence="50"/>
        <menuitem id="reports"
                  name="Reporting"
                  parent="alfa.replenishment"
                  sequence="2"/>


    </data>
</odoo>
