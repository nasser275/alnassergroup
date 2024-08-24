# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
	"name" : "Inter Warehouse Transfer",
	"version" : "15.0.0.0",
	"category" : "Warehouse",
	'summary': 'Inter warehouse stock transfer inter stock transfer internal stock transfer internal warehouse transfer internal warehouse stock transfer inter company transfer inter company stock transfer for multi warehouse stock transfer warehouse stock movement stock',
	"description": """
		Inter warehouse transfer odoo app helps user to manage inter stock location transfer, user can transfer stock from source location to destination location and reverse stock inter transfer, User can also change stock location for inter warehouse transfer.
	""",
	"author": "BrowseInfo",
	"website" : "https://www.browseinfo.in",
	"price": 49,
	"currency": 'EUR',
	"depends" : ['base','stock','portal','branch'],
	"data": [
		'security/ir.model.access.csv',
		'security/interwarehouse_groups.xml',
		'wizard/change_location_view.xml',
		'wizard/rec_qiz.xml',
		'wizard/return_rec_qiz.xml',
		'data/transfer_sequence.xml',
		'views/inter_warehouse_view.xml',
		'views/stock_view.xml',
		'views/return_inter_warehouse_view.xml',
		
	],
	'qweb': [
	],
    'license':'OPL-1',
	"auto_install": False,
	"installable": True,
	"live_test_url":'https://youtu.be/tar8-XQFd8U',
	"images":["static/description/Banner.png"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
