// Copyright (c) 2024, Rayan Soft Land and contributors
// For license information, please see license.txt
//frappe.provide("erpnext.accounts.dimensions");
//{% include 'erpnext/public/js/controllers/buying.js' %};
frappe.ui.form.on('PMS Bid Preparation', {
	setup: function(frm) {
		frm.custom_make_buttons = {
			'Purchase Order': 'Purchase Order',
			'Request for Quotation': 'Request for Quotation',
			'Supplier Quotation': 'Supplier Quotation',
			'Purchase Receipt': 'Purchase Receipt'
		};
		frm.set_query("project", function(doc) {
			return {
				filters: {'project_type': doc.project_type}
			};
		});
		// formatter for material request item
		// frm.set_indicator_formatter('item_code',
		// 	function(doc) { return (doc.stock_qty<=doc.ordered_qty) ? "green" : "orange"; });

		// frm.set_query("item_code", "items", function() {
		// 	return {
		// 		query: "erpnext.controllers.queries.item_query"
		// 	};
		// });

		// frm.set_query("from_warehouse", "items", function(doc) {
		// 	return {
		// 		filters: {'company': doc.company}
		// 	};
		// });

		// frm.set_query("bom_no", "items", function(doc, cdt, cdn) {
		// 	var row = locals[cdt][cdn];
		// 	return {
		// 		filters: {
		// 			"item": row.item_code
		// 		}
		// 	}
		// });
	},

	// onload: function(frm) {
	// 	// add item, if previous view was item
	// 	erpnext.utils.add_item(frm);

	
	// },

	
	// onload_post_render: function(frm) {
	// 	frm.get_field("items").grid.set_multiple_add("item_code", "qty");
	// },

	refresh: function(frm) {
	frm.events.make_custom_buttons(frm);
//		frm.toggle_reqd('customer', frm.doc.material_request_type=="Customer Provided");
	},
	make_custom_buttons: function(frm) {
		// if (frm.doc.docstatus==0) {
		// 	frm.add_custom_button(__("Bill of Materials"),
		// 		() => frm.events.get_items_from_bom(frm), __("Get Items From"));
		// }

		if (frm.doc.docstatus == 1 && frm.doc.status != 'Stopped') {
			let precision = frappe.defaults.get_default("float_precision");

			// if (flt(frm.doc.per_received, precision) < 100) {
			// 	frm.add_custom_button(__('Stop'),
			// 		() => frm.events.update_status(frm, 'Stopped'));
			// }

			//if (flt(frm.doc.per_ordered, precision) < 100) {
				let add_create_pick_list_button = () => {
					frm.add_custom_button(__('Pick List'),
						() => frm.events.create_pick_list(frm), __('Create'));
				}

					
					frm.add_custom_button(__('Quotation Approve'),
						() => frm.events.make_purchase_order(frm), __('Create'));
				

				
					frm.add_custom_button(__("Send Bid To Contractor"),
						() => frm.events.make_request_for_quotation(frm), __('Create'));
				

				
					frm.add_custom_button(__("Qutation Reveiw"),
						() => frm.events.make_supplier_quotation(frm), __('Create'));
				

				 

				frm.page.set_inner_btn_group_as_primary(__('Create'));
			//}
		}

		if (frm.doc.docstatus===0) {
			frm.add_custom_button(__('Sales Order'), () => frm.events.get_items_from_sales_order(frm),
				__("Get Items From"));
		}

		if (frm.doc.docstatus == 1 && frm.doc.status == 'Stopped') {
			frm.add_custom_button(__('Re-open'), () => frm.events.update_status(frm, 'Submitted'));
		}
	},

	update_status: function(frm, stop_status) {
		frappe.call({
			method: 'pms.pms_tender.doctype.pms_bid_preparation.pms_bid_preparation.update_status',
			args: { name: frm.doc.name, status: stop_status },
			callback(r) {
				if (!r.exc) {
					frm.reload_doc();
				}
			}
		});
	},

	// get_item_data: function(frm, item, overwrite_warehouse=false) {
	// 	if (item && !item.item_code) { return; }
	// 	frm.call({
	// 		method: "erpnext.stock.get_item_details.get_item_details",
	// 		child: item,
	// 		args: {
	// 			args: {
	// 				item_code: item.item_code,
	// 				from_warehouse: item.from_warehouse,
	// 				warehouse: item.warehouse,
	// 				doctype: frm.doc.doctype,
	// 				buying_price_list: frappe.defaults.get_default('buying_price_list'),
	// 				currency: frappe.defaults.get_default('Currency'),
	// 				name: frm.doc.name,
	// 				qty: item.qty || 1,
	// 				stock_qty: item.stock_qty,
	// 				company: frm.doc.company,
	// 				conversion_rate: 1,
	// 				material_request_type: frm.doc.material_request_type,
	// 				plc_conversion_rate: 1,
	// 				rate: item.rate,
	// 				uom: item.uom,
	// 				conversion_factor: item.conversion_factor,
	// 				project: item.project,
	// 			},
	// 			overwrite_warehouse: overwrite_warehouse
	// 		},
	// 		callback: function(r) {
	// 			const d = item;
	// 			const qty_fields = ['actual_qty', 'projected_qty', 'min_order_qty'];

	// 			if(!r.exc) {
	// 				$.each(r.message, function(k, v) {
	// 					if(!d[k] || in_list(qty_fields, k)) d[k] = v;
	// 				});
	// 			}
	// 		}
	// 	});
	// },

	project: function(frm) {
		if(!frm.doc.project) frappe.throw(__("Company field is required"));
		frappe.call({
			method: "pms.pms_tender.doctype.pms_bid_preparation.pms_bid_preparation.get_project_tasks",
			args: {
				project:frm.doc.project,

			},
			callback: function(r) {
				if (!r.message) {
					frappe.throw(__("Project does not contain any task"));
				} else {
					erpnext.utils.remove_empty_first_row(frm, "items");
					$.each(r.message, function(i, task) {
						var d = frappe.model.add_child(cur_frm.doc, "PMS Bid Preparation", "items");
						d.task_code = task.name;
						d.task_name = task.subject;
						// d.description = task.description;
						// d.warehouse = values.warehouse;
						// d.uom = task.stock_uom;
						// d.stock_uom = task.stock_uom;
						// d.conversion_factor = 1;
						// d.qty = task.qty;
						// d.project = task.project;
					});
				}
				refresh_field("items");
			}
		});
	},

	make_purchase_order: function(frm) {
		frappe.prompt(
			{
				label: __('For Default Supplier (Optional)'),
				fieldname:'default_supplier',
				fieldtype: 'Link',
				options: 'Supplier',
				description: __('Select a Supplier from the Default Suppliers of the items below. On selection, a Purchase Order will be made against items belonging to the selected Supplier only.'),
				get_query: () => {
					return{
						query: "pms.pms_tender.doctype.pms_bid_preparation.pms_bid_preparation.get_default_supplier_query",
						filters: {'doc': frm.doc.name}
					}
				}
			},
			(values) => {
				frappe.model.open_mapped_doc({
					method: "pms.pms_tender.doctype.pms_bid_preparation.pms_bid_preparation.make_purchase_order",
					frm: frm,
					args: { default_supplier: values.default_supplier },
					run_link_triggers: true
				});
			},
			__('Enter Supplier'),
			__('Create')
		)
	},

	make_request_for_quotation: function(frm) {
		frappe.model.open_mapped_doc({
			method: "pms.pms_tender.doctype.pms_bid_preparation.pms_bid_preparation.make_request_for_quotation",
			frm: frm,
			run_link_triggers: true
		});
	},

	make_supplier_quotation: function(frm) {
		frappe.model.open_mapped_doc({
			method: "pms.pms_tender.doctype.pms_bid_preparation.pms_bid_preparation.make_supplier_quotation",
			frm: frm
		});
	},

	

	
});

// frappe.ui.form.on("Material Request Item", {
// 	qty: function (frm, doctype, name) {
// 		const item = locals[doctype][name];
// 		if (flt(item.qty) < flt(item.min_order_qty)) {
// 			frappe.msgprint(__("Warning: Material Requested Qty is less than Minimum Order Qty"));
// 		}
// 		frm.events.get_item_data(frm, item, false);
// 	},

// 	from_warehouse: function(frm, doctype, name) {
// 		const item = locals[doctype][name];
// 		frm.events.get_item_data(frm, item, false);
// 	},

// 	warehouse: function(frm, doctype, name) {
// 		const item = locals[doctype][name];
// 		frm.events.get_item_data(frm, item, false);
// 	},

// 	rate: function(frm, doctype, name) {
// 		const item = locals[doctype][name];
// 		frm.events.get_item_data(frm, item, false);
// 	},

// 	item_code: function(frm, doctype, name) {
// 		const item = locals[doctype][name];
// 		item.rate = 0;
// 		item.uom = '';
// 		set_schedule_date(frm);
// 		frm.events.get_item_data(frm, item, true);
// 	},

// 	schedule_date: function(frm, cdt, cdn) {
// 		var row = locals[cdt][cdn];
// 		if (row.schedule_date) {
// 			if(!frm.doc.schedule_date) {
// 				erpnext.utils.copy_value_in_all_rows(frm.doc, cdt, cdn, "items", "schedule_date");
// 			} else {
// 				set_schedule_date(frm);
// 			}
// 		}
// 	}
// });

