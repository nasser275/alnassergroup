


odoo.define('hide_archive_unarchive_buttons.BasicView', function (require) {
"use strict";
  var session = require('web.session');
  var BasicView = require('web.BasicView');
  BasicView.include({
    init: function(viewInfo, params) {
      var self = this;
      this._super.apply(this, arguments);
      var model = self.controllerParams.modelName in ['res.partner','sale.order','account.move','pos.session','pos.order','alfa.replenishment','return.replenishment','product.product','product.template'] ? 'True' : 'False';
      if(model) {
        session.user_has_group('hide_archive_unarchive_buttons.group_archive_user').then(function(has_group) {
          if(!has_group) {
            self.controllerParams.archiveEnabled = 'False' in viewInfo.fields;
          }
        });
      }
    },
  });
});