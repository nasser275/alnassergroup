odoo.define('import_access.import', function (require) {
    "use strict";

    const ImportMenu = require('base_import.ImportMenu');
    const FavoriteMenu = require('web.FavoriteMenu');
    const {useModel} = require('web.Model');
    var session = require('web.session');

    const {Component} = owl;
    const {useState} = owl.hooks;

    /**
     * Import Records menu
     *
     * This component is used to import the records for particular model.
     */
    class CustomImportMenu extends ImportMenu {

        constructor() {
            super(...arguments);
            this.model = useModel('searchModel');
            this.state = useState({
                data: {
                    milestones: {
                        data: []
                    },
                    user: {
                        'group_import_access': true
                    },
                }
            });
        }

        async willStart() {
            await session.user_has_group('import_access.group_import_access').then(hasGroup => {
                this.state.data.user.group_import_access=hasGroup;
            });

        }

        //---------------------------------------------------------------------
        // Handlers
        //---------------------------------------------------------------------

        /**
         * @private
         */
        importRecords() {
            const action = {
                type: 'ir.actions.client',
                tag: 'import',
                params: {
                    model: this.model.config.modelName,
                    context: this.model.config.context,
                }
            };
            this.trigger('do-action', {action: action});
        }

        //---------------------------------------------------------------------
        // Static
        //---------------------------------------------------------------------

        /**
         * @param {Object} env
         * @returns {boolean}
         */
        static shouldBeDisplayed(env) {
            return env.view &&
                ['kanban', 'list'].includes(env.view.type) &&
                env.action.type === 'ir.actions.act_window' &&
                !env.device.isMobile &&
                !!JSON.parse(env.view.arch.attrs.import || '1') &&
                !!JSON.parse(env.view.arch.attrs.create || '1');

        }
    }

    CustomImportMenu.props = {};
    CustomImportMenu.template = "base_import.ImportRecords";

    FavoriteMenu.registry.add('import-menu', CustomImportMenu, 1);

    return CustomImportMenu;


});