# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# ERPNext - web based ERP (http://erpnext.com)
# For license information, please see license.txt


import json

import frappe
from frappe import _, msgprint
from frappe.model.mapper import get_mapped_doc
from frappe.query_builder.functions import Sum
from frappe.utils import cint, cstr, flt, get_link_to_form, getdate, new_line_sep, nowdate

from erpnext.buying.utils import check_on_hold_or_closed_status, validate_for_items
from erpnext.controllers.buying_controller import BuyingController
from erpnext.manufacturing.doctype.work_order.work_order import get_item_details
from erpnext.stock.doctype.item.item import get_item_defaults
from erpnext.stock.stock_balance import get_indented_qty, update_bin_qty
from frappe.model.document import Document

# form_grid_templates = {"items": "templates/form_grid/material_request_grid.html"}


class PMSBidPreparation(Document):

	
	#def validate(self):
		# super(PMSBidPreparation, self).validate()


		# if not self.status:
		# 	self.status = "Draft"

		# from erpnext.controllers.status_updater import validate_status

		# validate_status(
		# 	self.status,
		# 	[
		# 		"Draft",
		# 		"Submitted",
		# 		"Stopped",
		# 		"Cancelled",
		# 		"Pending",
		# 		"Partially Ordered",
		# 		"Ordered",
		# 		"Issued",
		# 		"Transferred",
		# 		"Received",
		# 	],
		# )

		
		# self.set_title()
		# # self.validate_qty_against_so()
		# # NOTE: Since Item BOM and FG quantities are combined, using current data, it cannot be validated
		# # Though the creation of Material Request from a Production Plan can be rethought to fix this

	

	# def before_update_after_submit(self):
	# 	self.validate_schedule_date()

	# def validate_material_request_type(self):
	# 	"""Validate fields in accordance with selected type"""

	# 	if self.material_request_type != "Customer Provided":
	# 		self.customer = None

	# def set_title(self):
	# 	if not self.title:
	# 		items = ", ".join([d.item_name for d in self.items][:3])
	# 		self.title = _("{0} Request for {1}").format(self.material_request_type, items)[:100]
	def set_status(self,update=None,status=None):
		return
	def on_submit(self):
		# self.update_requested_qty_in_production_plan()
		# self.update_requested_qty()
		# if self.material_request_type == "Purchase":
		# 	self.validate_budget()
		return

	def before_save(self):
		self.set_status(update=True)

	def before_submit(self):
		self.set_status(update=True)

	def before_cancel(self):
		# if MRQ is already closed, no point saving the document
		check_on_hold_or_closed_status(self.doctype, self.name)

		self.set_status(update=True, status="Cancelled")

	def check_modified_date(self):
		mod_db = frappe.db.sql(
			"""select modified from `tabMaterial Request` where name = %s""", self.name
		)
		date_diff = frappe.db.sql(
			"""select TIMEDIFF('%s', '%s')""" % (mod_db[0][0], cstr(self.modified))
		)

		if date_diff and date_diff[0][0]:
			frappe.throw(_("{0} {1} has been modified. Please refresh.").format(_(self.doctype), self.name))

	def update_status(self, status):
		self.check_modified_date()
		self.status_can_change(status)
		self.set_status(update=True, status=status)
		self.update_requested_qty()

	def status_can_change(self, status):
		"""
		validates that `status` is acceptable for the present controller status
		and throws an Exception if otherwise.
		"""
		if self.status and self.status == "Cancelled":
			# cancelled documents cannot change
			if status != self.status:
				frappe.throw(
					_("{0} {1} is cancelled so the action cannot be completed").format(
						_(self.doctype), self.name
					),
					frappe.InvalidStatusError,
				)

		elif self.status and self.status == "Draft":
			# draft document to pending only
			if status != "Pending":
				frappe.throw(
					_("{0} {1} has not been submitted so the action cannot be completed").format(
						_(self.doctype), self.name
					),
					frappe.InvalidStatusError,
				)

	def on_cancel(self):
		self.update_requested_qty_in_production_plan()
		self.update_requested_qty()

	

def set_missing_values(source, target_doc):
	if target_doc.doctype == "Purchase Order" and getdate(target_doc.schedule_date) < getdate(
		nowdate()
	):
		target_doc.schedule_date = None
	target_doc.run_method("set_missing_values")
	target_doc.run_method("calculate_taxes_and_totals")


def update_item(obj, target, source_parent):
	target.conversion_factor = obj.conversion_factor
	target.qty = flt(flt(obj.stock_qty) - flt(obj.ordered_qty)) / target.conversion_factor
	target.stock_qty = target.qty * target.conversion_factor
	if getdate(target.schedule_date) < getdate(nowdate()):
		target.schedule_date = None


def get_list_context(context=None):
	from erpnext.controllers.website_list_for_contact import get_list_context

	list_context = get_list_context(context)
	list_context.update(
		{
			"show_sidebar": True,
			"show_search": True,
			"no_breadcrumbs": True,
			"title": _("Material Request"),
		}
	)

	return list_context


@frappe.whitelist()
def update_status(name, status):
	material_request = frappe.get_doc("Material Request", name)
	material_request.check_permission("write")
	material_request.update_status(status)


@frappe.whitelist()
def make_purchase_order(source_name, target_doc=None, args=None):
	if args is None:
		args = {}
	if isinstance(args, str):
		args = json.loads(args)

	def postprocess(source, target_doc):
		if frappe.flags.args and frappe.flags.args.default_supplier:
			# items only for given default supplier
			supplier_items = []
			for d in target_doc.items:
				default_supplier = get_item_defaults(d.item_code, target_doc.company).get("default_supplier")
				if frappe.flags.args.default_supplier == default_supplier:
					supplier_items.append(d)
			target_doc.items = supplier_items

		set_missing_values(source, target_doc)

	def select_item(d):
		filtered_items = args.get("filtered_children", [])
		child_filter = d.name in filtered_items if filtered_items else True

		return d.ordered_qty < d.stock_qty and child_filter

	doclist = get_mapped_doc(
		"Material Request",
		source_name,
		{
			"Material Request": {
				"doctype": "Purchase Order",
				"validation": {"docstatus": ["=", 1], "material_request_type": ["=", "Purchase"]},
			},
			"Material Request Item": {
				"doctype": "Purchase Order Item",
				"field_map": [
					["name", "material_request_item"],
					["parent", "material_request"],
					["uom", "stock_uom"],
					["uom", "uom"],
					["sales_order", "sales_order"],
					["sales_order_item", "sales_order_item"],
					["wip_composite_asset", "wip_composite_asset"],
				],
				"postprocess": update_item,
				"condition": select_item,
			},
		},
		target_doc,
		postprocess,
	)

	return doclist


@frappe.whitelist()
def make_bid_to_contractor(source_name, target_doc=None):
	doclist = get_mapped_doc(
		"PMS Bid Preparation",
		source_name,
		{
			"PMS Bid Preparation": {
				"doctype": "PMS Send Bid to Contractor",
				"validation": {"docstatus": ["=", 1]},
			},
			"PMS Bid Preparation Item": {
				"doctype": "PMS Send Bid to Contractor Item",
				"field_map": [
					["name", "material_request_item"],
					["parent", "material_request"],
					["uom", "uom"],
				],
			},
		},
		target_doc,
	)

	return doclist


@frappe.whitelist()
def make_purchase_order_based_on_supplier(source_name, target_doc=None, args=None):
	mr = source_name

	supplier_items = get_items_based_on_default_supplier(args.get("supplier"))

	def postprocess(source, target_doc):
		target_doc.supplier = args.get("supplier")
		if getdate(target_doc.schedule_date) < getdate(nowdate()):
			target_doc.schedule_date = None
		target_doc.set(
			"items",
			[
				d for d in target_doc.get("items") if d.get("item_code") in supplier_items and d.get("qty") > 0
			],
		)

		set_missing_values(source, target_doc)

	target_doc = get_mapped_doc(
		"Material Request",
		mr,
		{
			"Material Request": {
				"doctype": "Purchase Order",
			},
			"Material Request Item": {
				"doctype": "Purchase Order Item",
				"field_map": [
					["name", "material_request_item"],
					["parent", "material_request"],
					["uom", "stock_uom"],
					["uom", "uom"],
				],
				"postprocess": update_item,
				"condition": lambda doc: doc.ordered_qty < doc.qty,
			},
		},
		target_doc,
		postprocess,
	)

	return target_doc




@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_material_requests_based_on_supplier(doctype, txt, searchfield, start, page_len, filters):
	conditions = ""
	if txt:
		conditions += "and mr.name like '%%" + txt + "%%' "

	if filters.get("transaction_date"):
		date = filters.get("transaction_date")[1]
		conditions += "and mr.transaction_date between '{0}' and '{1}' ".format(date[0], date[1])

	supplier = filters.get("supplier")
	supplier_items = get_items_based_on_default_supplier(supplier)

	if not supplier_items:
		frappe.throw(_("{0} is not the default supplier for any items.").format(supplier))

	material_requests = frappe.db.sql(
		"""select distinct mr.name, transaction_date,company
		from `tabMaterial Request` mr, `tabMaterial Request Item` mr_item
		where mr.name = mr_item.parent
			and mr_item.item_code in ({0})
			and mr.material_request_type = 'Purchase'
			and mr.per_ordered < 99.99
			and mr.docstatus = 1
			and mr.status != 'Stopped'
			and mr.company = %s
			{1}
		order by mr_item.item_code ASC
		limit {2} offset {3} """.format(
			", ".join(["%s"] * len(supplier_items)), conditions, cint(page_len), cint(start)
		),
		tuple(supplier_items) + (filters.get("company"),),
		as_dict=1,
	)

	return material_requests


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_default_supplier_query(doctype, txt, searchfield, start, page_len, filters):
	doc = frappe.get_doc("Material Request", filters.get("doc"))
	item_list = []
	for d in doc.items:
		item_list.append(d.item_code)

	return frappe.db.sql(
		"""select default_supplier
		from `tabItem Default`
		where parent in ({0}) and
		default_supplier IS NOT NULL
		""".format(
			", ".join(["%s"] * len(item_list))
		),
		tuple(item_list),
	)


@frappe.whitelist()
def make_supplier_quotation(source_name, target_doc=None):
	def postprocess(source, target_doc):
		set_missing_values(source, target_doc)

	doclist = get_mapped_doc(
		"Material Request",
		source_name,
		{
			"Material Request": {
				"doctype": "Supplier Quotation",
				"validation": {"docstatus": ["=", 1], "material_request_type": ["=", "Purchase"]},
			},
			"Material Request Item": {
				"doctype": "Supplier Quotation Item",
				"field_map": {
					"name": "material_request_item",
					"parent": "material_request",
					"sales_order": "sales_order",
				},
			},
		},
		target_doc,
		postprocess,
	)

	return doclist




@frappe.whitelist()
def create_pick_list(source_name, target_doc=None):
	doc = get_mapped_doc(
		"Material Request",
		source_name,
		{
			"Material Request": {
				"doctype": "Pick List",
				"field_map": {"material_request_type": "purpose"},
				"validation": {"docstatus": ["=", 1]},
			},
			"Material Request Item": {
				"doctype": "Pick List Item",
				"field_map": {"name": "material_request_item", "qty": "stock_qty"},
			},
		},
		target_doc,
	)

	doc.set_item_locations()

	return doc


@frappe.whitelist()
def make_in_transit_stock_entry(source_name, in_transit_warehouse):
	ste_doc = make_stock_entry(source_name)
	ste_doc.add_to_transit = 1
	ste_doc.to_warehouse = in_transit_warehouse

	for row in ste_doc.items:
		row.t_warehouse = in_transit_warehouse

	return ste_doc

@frappe.whitelist()
def get_project_tasks(project):
	mr = frappe.db.get_all("Task",filters={"project":project}
	,fields={"name","subject"}
	)
	return mr
