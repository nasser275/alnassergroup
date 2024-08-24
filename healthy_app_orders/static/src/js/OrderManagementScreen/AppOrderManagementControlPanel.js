odoo.define('app_list.AppOrderManagementControlPanel', function (require) {
    'use strict';

    const { useContext } = owl.hooks;
    const { useAutofocus, useListener } = require('web.custom_hooks');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const AppOrderFetcher = require('app_list.AppOrderFetcher');
    const contexts = require('point_of_sale.PosContext');

    // NOTE: These are constants so that they are only instantiated once
    // and they can be used efficiently by the OrderManagementControlPanel.
    const VALID_SEARCH_TAGS = new Set(['order_date', 'customer', 'client', 'name', 'order']);
    const FIELD_MAP = {
        date: 'order_date',
        customer: 'partner_id.display_name',
        client: 'partner_id.display_name',
        name: 'name',
        order: 'name',
    };
    const SEARCH_FIELDS = ['name', 'partner_id.display_name', 'order_date'];

    /**
     * @emits close-screen
     * @emits prev-page
     * @emits next-page
     * @emits search
     */
    class AppOrderManagementControlPanel extends PosComponent {
        constructor() {
            super(...arguments);
            // We are using context because we want the `searchString` to be alive
            // even if this component is destroyed (unmounted).
            this.orderManagementContext = useContext(contexts.orderManagement);
            useListener('clear-search', this._onClearSearch);
            useAutofocus({ selector: 'input' });

            let currentClient = this.env.pos.get_client();
            if (currentClient) {
                this.orderManagementContext.searchString = currentClient.name;
                let domain = this._computeDomain();
                AppOrderFetcher.setSearchDomain(domain);
            }
        }
        onInputKeydown(event) {
            if (event.key === 'Enter') {
                this.trigger('search', this._computeDomain());
            }
        }
        get showPageControls() {
            return AppOrderFetcher.lastPage > 1;
        }
        get pageNumber() {
            const currentPage = AppOrderFetcher.currentPage;
            const lastPage = AppOrderFetcher.lastPage;
            return isNaN(lastPage) ? '' : `(${currentPage}/${lastPage})`;
        }
        get validSearchTags() {
            return VALID_SEARCH_TAGS;
        }
        get fieldMap() {
            return FIELD_MAP;
        }
        get searchFields() {
            return SEARCH_FIELDS;
        }
        _computeDomain() {
            let domain = [['state', '!=', 'cancel'],['created_from_schedule', '=', false],['deleted', '=', false]];
            const input = this.orderManagementContext.searchString.trim();
            if (!input) return domain;

            const searchConditions = this.orderManagementContext.searchString.split(/[,&]\s*/);
            if (searchConditions.length === 1) {
                let cond = searchConditions[0].split(/:\s*/);
                if (cond.length === 1) {
                  domain = domain.concat(Array(this.searchFields.length - 1).fill('|'));
                  domain = domain.concat(this.searchFields.map((field) => [field, 'ilike', `%${cond[0]}%`]));
                  return domain;
                }
            }

            for (let cond of searchConditions) {
                let [tag, value] = cond.split(/:\s*/);
                if (!this.validSearchTags.has(tag)) continue;
                domain.push([this.fieldMap[tag], 'ilike', `%${value}%`]);
            }
            return domain;
        }
        _onClearSearch() {
            this.orderManagementContext.searchString = '';
            this.onInputKeydown({ key: 'Enter' });
        }
    }
    AppOrderManagementControlPanel.template = 'AppOrderManagementControlPanel';

    Registries.Component.add(AppOrderManagementControlPanel);

    return AppOrderManagementControlPanel;
});
