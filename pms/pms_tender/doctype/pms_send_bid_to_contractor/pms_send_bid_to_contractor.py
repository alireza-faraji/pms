# Copyright (c) 2024, Rayan Soft Land and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _, msgprint
from frappe.model.mapper import get_mapped_doc
from erpnext.accounts.party import get_party_account_currency, get_party_details
#from erpnext.stock.doctype.material_request.material_request import set_missing_values

class PMSSendBidtoContractor(Document):
	def on_submit(self):
		return
@frappe.whitelist()
def make_supplier_quotation_from_pms_rfq(source_name, target_doc=None, for_supplier=None):
	def postprocess(source, target_doc):
		if for_supplier:
			target_doc.supplier = for_supplier
			args = get_party_details(for_supplier, party_type="Supplier", ignore_permissions=True)
			target_doc.currency = args.currency or get_party_account_currency(
				"Supplier", for_supplier, source.company
			)
			target_doc.buying_price_list = args.buying_price_list or frappe.db.get_value(
				"Buying Settings", None, "buying_price_list"
			)
		#set_missing_values(source, target_doc)

	doclist = get_mapped_doc(
		"PMS Send Bid to Contractor",
		source_name,
		{
			"PMS Send Bid to Contractor": {
				"doctype": "PMS Qutation Reveiw",
				"validation": {"docstatus": ["=", 1]},
			},
			"PMS Send Bid to Contractor Item": {
				"doctype": "PMS Qutation Reveiw Item",
				"field_map": {"name": "pms_send_bid_to_contractor_item", "parent": "pms_send_bid_to_contractor"},
			},
		},
		target_doc,
		postprocess,
	)

	return doclist

@frappe.whitelist()
def test(source_name, target_doc=None, for_supplier=None):
	frappe.msgprint("test");
	return 
