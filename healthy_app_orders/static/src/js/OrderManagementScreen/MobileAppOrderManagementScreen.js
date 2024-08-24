odoo.define('point_of_sale.MobileAppOrderManagementScreen', function (require) {
    const SaleOrderManagementScreen = require('app_list.SaleOrderManagementScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    const { useState } = owl.hooks;

    const MobileAppOrderManagementScreen = (SaleOrderManagementScreen) => {
        class MobileAppOrderManagementScreen extends SaleOrderManagementScreen {
            constructor() {
                super(...arguments);
                useListener('click-order', this._onShowDetails)
                this.mobileState = useState({ showDetails: false });
            }
            _onShowDetails() {
                this.mobileState.showDetails = true;
            }
        }
        MobileAppOrderManagementScreen.template = 'MobileAppOrderManagementScreen';
        return MobileAppOrderManagementScreen;
    };

    Registries.Component.addByExtending(MobileAppOrderManagementScreen, SaleOrderManagementScreen);

    return MobileAppOrderManagementScreen;
});
