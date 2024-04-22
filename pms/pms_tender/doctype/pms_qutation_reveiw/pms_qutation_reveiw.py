# Copyright (c) 2024, Rayan Soft Land and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, getdate, nowdate
class PMSQutationReveiw(Document):
	def validate(self):
	 

		if not self.status:
			self.status = "Draft"

		from erpnext.controllers.status_updater import validate_status

		validate_status(self.status, ["Draft", "Submitted", "Stopped", "Cancelled"])

		 

	def on_submit(self):
		self.db_set("status", "Submitted")
		self.update_rfq_supplier_status(1)

	def on_cancel(self):
		self.db_set("status", "Cancelled")
		self.update_rfq_supplier_status(0)

	def on_trash(self):
		pass
	def update_rfq_supplier_status(self, include_me):
		rfq_list = set([])
		# for item in self.items:
		# 	if item.request_for_quotation:
		# 		rfq_list.add(item.request_for_quotation)
		# for rfq in rfq_list:
		# 	doc = frappe.get_doc("Request for Quotation", rfq)
		# 	doc_sup = frappe.get_all(
		# 		"Request for Quotation Supplier",
		# 		filters={"parent": doc.name, "supplier": self.supplier},
		# 		fields=["name", "quote_status"],
		# 	)

		# 	doc_sup = doc_sup[0] if doc_sup else None
		# 	if not doc_sup:
		# 		frappe.throw(
		# 			_("Supplier {0} not found in {1}").format(
		# 				self.supplier,
		# 				"<a href='desk/app/Form/Request for Quotation/{0}'> Request for Quotation {0} </a>".format(
		# 					doc.name
		# 				),
		# 			)
		# 		)

		# 	quote_status = _("Received")
		# 	for item in doc.items:
		# 		sqi_count = frappe.db.sql(
		# 			"""
		# 			SELECT
		# 				COUNT(sqi.name) as count
		# 			FROM
		# 				`tabSupplier Quotation Item` as sqi,
		# 				`tabSupplier Quotation` as sq
		# 			WHERE sq.supplier = %(supplier)s
		# 				AND sqi.docstatus = 1
		# 				AND sq.name != %(me)s
		# 				AND sqi.request_for_quotation_item = %(rqi)s
		# 				AND sqi.parent = sq.name""",
		# 			{"supplier": self.supplier, "rqi": item.name, "me": self.name},
		# 			as_dict=1,
		# 		)[0]
		# 		self_count = (
		# 			sum(my_item.request_for_quotation_item == item.name for my_item in self.items)
		# 			if include_me
		# 			else 0
		# 		)
		# 		if (sqi_count.count + self_count) == 0:
		# 			quote_status = _("Pending")

		# 		frappe.db.set_value(
		# 			"Request for Quotation Supplier", doc_sup.name, "quote_status", quote_status
		# 		)
@frappe.whitelist()
def make_quotation_approve(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.run_method("set_missing_values")
		target.run_method("get_schedule_dates")
		target.run_method("calculate_taxes_and_totals")

	#def update_item(obj, target, source_parent):
	# 	target.stock_qty = flt(obj.qty) * flt(obj.conversion_factor)

	doclist = get_mapped_doc(
		"PMS Qutation Reveiw",
		source_name,
		{
			"PMS Qutation Reveiw": {
				"doctype": "PMS Quotation Approve",
				"validation": {
					"docstatus": ["=", 1],
				},
			},
			"PMS Qutation Reveiw Item": {
				"doctype": "PMS Quotation Approve Item",
				"field_map": [
					["name", "pms_qutation_reveiw_item"],
					["parent", "pms_qutation_reveiw"],
					["pms_bid_preparation", "pms_bid_preparation"],
					["pms_bid_preparation_item", "pms_bid_preparation_item"],
					#["sales_order", "sales_order"],
				],
				#"postprocess": update_item,
			},
			# "Purchase Taxes and Charges": {
			# 	"doctype": "Purchase Taxes and Charges",
			# },
		},
		target_doc,
		set_missing_values,
	)

	doclist.set_onload("ignore_price_list", True)
	return doclist
