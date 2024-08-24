# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "POS Order Backup/Restore",
  "summary"              :  """This module allows the POS User to Backup Orders and Restore the POS Orders whenever an error appears during a session. User can Restore Orders that were created in the POS Session. Order data can be restored from the JSON File / JSON Data.Backup Data|Backup Offline Data|POS Offline Orders|Offline Orders Backup.""",
  "category"             :  "Point Of Sale",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com",
  "description"          :  """This module allows the POS User to Backup and Restore the POS Orders whenever an error appears during a session.""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=pos_order_backup&custom_url=/pos/web/#action=pos.ui",
  "depends"              :  [
                             'point_of_sale',
                             'wk_wizard_messages',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/point_of_sale_view.xml',
                             'wizard/import_orders_wizard_view.xml',
                            ],
  "assets"               :  {
                              'point_of_sale.assets': [
                                "/pos_order_backup/static/src/js/chrome.js",
                                "/pos_order_backup/static/src/js/popups.js",
                                "/pos_order_backup/static/src/js/db.js",
                                "/pos_order_backup/static/src/css/pos_order_backup.css",
                              ],
                              'web.assets_qweb': [
                                'pos_order_backup/static/src/xml/**/*',
                              ],
                            },
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  69,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}