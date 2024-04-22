// Copyright (c) 2024, Rayan Soft Land and contributors
// For license information, please see license.txt

frappe.ui.form.on('PMS Qutation Reveiw', {
	setup: function(frm) {
		frm.custom_make_buttons = {
			'Quotation Approve': 'Create'
		}

		 
	},
	refresh: function(frm, cdt, cdn) {
		 
		if (frm.doc.__islocal && !frm.doc.valid_till) {
			frm.set_value('valid_till', frappe.datetime.add_months(frm.doc.transaction_date, 1));
		}

		if(frm.doc.docstatus === 1) {

			frm.add_custom_button(__('Quotation Reveiw'),
				function(){ frm.trigger("make_quotation_approve") }, __("Create"));

			frm.page.set_inner_btn_group_as_primary(__('Create'));
			 
		}
		// else if (frm.doc.docstatus===0) {

		// 	frm.add_custom_button(__('Material Request'),
		// 		function() {
		// 			erpnext.utils.map_current_doc({
		// 				method: "erpnext.stock.doctype.material_request.material_request.make_supplier_quotation",
		// 				source_doctype: "Material Request",
		// 				target: me.frm,
		// 				setters: {
		// 					schedule_date: undefined,
		// 					status: undefined
		// 				},
		// 				get_query_filters: {
		// 					material_request_type: "Purchase",
		// 					docstatus: 1,
		// 					status: ["!=", "Stopped"],
		// 					per_ordered: ["<", 100],
		// 					company: me.frm.doc.company
		// 				}
		// 			})
		// 		}, __("Get Items From"));

		// 	// Link Material Requests
		// 	frm.add_custom_button(__('Link to Material Requests'),
		// 		function() {
		// 			erpnext.buying.link_to_mrs(me.frm);
		// 		}, __("Tools"));

		// 	frm.add_custom_button(__("Request for Quotation"),
		// 	function() {
		// 		if (!me.frm.doc.supplier) {
		// 			frappe.throw({message:__("Please select a Supplier"), title:__("Mandatory")})
		// 		}
		// 		erpnext.utils.map_current_doc({
		// 			method: "erpnext.buying.doctype.request_for_quotation.request_for_quotation.make_supplier_quotation_from_rfq",
		// 			source_doctype: "Request for Quotation",
		// 			target: me.frm,
		// 			setters: {
		// 				transaction_date: null
		// 			},
		// 			get_query_filters: {
		// 				supplier: me.frm.doc.supplier,
		// 				company: me.frm.doc.company
		// 			},
		// 			get_query_method: "erpnext.buying.doctype.request_for_quotation.request_for_quotation.get_rfq_containing_supplier"

		// 		})
		// 	}, __("Get Items From"));
		// }
	}
	,
	make_quotation_approve() {
		frappe.model.open_mapped_doc({
			method: "pms.pms_tender.doctype.pms_qutation_reveiw.pms_qutation_reveiw.make_quotation_approve",
			frm: cur_frm
		})
	}
	// ,make_quotation() {
	// 	frappe.model.open_mapped_doc({
	// 		method: "erpnext.buying.doctype.supplier_quotation.supplier_quotation.make_quotation",
	// 		frm: cur_frm
	// 	})

	// }
});
