odoo.define("disable_create_on_fly.Fly", function (require) {
    "use strict";

    var relational_fields = require('web.relational_fields');
    const {sprintf} = require("web.utils");
    var core = require('web.core');
    var data = require('web.data');
    var _t = core._t;
    const { escape } = owl.utils;

    relational_fields.FieldMany2One.include({

        _search: async function (searchValue = "") {
        const value = searchValue.trim();
        const domain = this.record.getDomain(this.recordParams);
        const context = Object.assign(
            this.record.getContext(this.recordParams),
            this.additionalContext
        );

        // Exclude black-listed ids from the domain
        const blackListedIds = this._getSearchBlacklist();
        if (blackListedIds.length) {
            domain.push(['id', 'not in', blackListedIds]);
        }

        const nameSearch = this._rpc({
            model: this.field.relation,
            method: "name_search",
            kwargs: {
                name: value,
                args: domain,
                operator: "ilike",
                limit: this.limit + 1,
                context,
            }
        });
        const results = await this.orderer.add(nameSearch);

        // Format results to fit the options dropdown
        let values = results.map((result) => {
            const [id, fullName] = result;
            const displayName = this._getDisplayName(fullName).trim();
            result[1] = displayName;
            return {
                id,
                label: escape(displayName) || data.noDisplayContent,
                value: displayName,
                name: displayName,
            };
        });

        // Add "Search more..." option if results count is higher than the limit
        if (this.limit < values.length) {
            values = this._manageSearchMore(values, value, domain, context);
        }

        // Additional options...
        const canQuickCreate = this.can_create && !this.nodeOptions.no_quick_create;
        const canCreateEdit = this.can_create && !this.nodeOptions.no_create_edit;
        if (value.length) {
            // "Quick create" option
            const nameExists = results.some((result) => result[1] === value);
            if (this.field.relation=='product.template' || this.field.relation=='product.product' ){

            }else{
             if (canQuickCreate && !nameExists) {
                 values.push({
                     label: sprintf(
                         _t(`Create "<strong>%s</strong>"`),
                         escape(value)
                     ),
                     action: () => this._quickCreate(value),
                     classname: 'o_m2o_dropdown_option'
                 });
             }
             if (canCreateEdit) {
                 const valueContext = this._createContext(value);
                 values.push({
                     label: _t("Create and Edit..."),
                     action: () => {
                         // Input value is cleared and the form popup opens
                         this.el.querySelector(':scope input').value = "";
                         return this._searchCreatePopup('form', false, valueContext);
                     },
                     classname: 'o_m2o_dropdown_option',
                 });
             }
            }

            // "No results" option
            if (!values.length) {
                values.push({
                    label: _t("No records"),
                    classname: 'o_m2o_no_result',
                });
            }
        } else if (!this.value && (canQuickCreate || canCreateEdit)) {
            // "Start typing" option
            values.push({
                label: _t("Start typing..."),
                classname: 'o_m2o_start_typing',
            });
        }

        return values;
    },




    });

});