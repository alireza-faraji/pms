// Copyright (c) 2024, Rayan Soft Land and contributors
// For license information, please see license.txt


	cur_frm.add_fetch('contact', 'email_id', 'email_id')

	frappe.ui.form.on('PMS Send Bid to Contractor', {
	setup: function(frm) {
		frm.custom_make_buttons = {
			'Supplier Quotation': 'Create'
		}

		frm.fields_dict["suppliers"].grid.get_field("contact").get_query = function(doc, cdt, cdn) {
			let d = locals[cdt][cdn];
			return {
				query: "frappe.contacts.doctype.contact.contact.contact_query",
				filters: {
					link_doctype: "Supplier",
					link_name: d.supplier || ""
				}
			};
		}

	
	},

	onload: function(frm) {
		if(!frm.doc.message_for_supplier) {
			frm.set_value("message_for_supplier", __("Please supply the specified items at the best possible rates"))
		}
	},

	refresh: function(frm, cdt, cdn) {
		if (frm.doc.docstatus === 1) {

			frm.add_custom_button(__('Supplier Quotation'),
				function(){ frm.trigger("make_supplier_quotation") }, __("Create"));


			frm.add_custom_button(__("Send Emails to Suppliers"), function() {
				frappe.call({
					method: 'erpnext.buying.doctype.request_for_quotation.request_for_quotation.send_supplier_emails',
					freeze: true,
					args: {
						rfq_name: frm.doc.name
					},
					callback: function(r){
						frm.reload_doc();
					}
				});
			}, __("Tools"));

			frm.add_custom_button(
				__("Download PDF"),
				() => {
					frappe.prompt(
						[
							{
								fieldtype: "Link",
								label: "Select a Supplier",
								fieldname: "supplier",
								options: "Supplier",
								reqd: 1,
								default: frm.doc.suppliers?.length == 1 ? frm.doc.suppliers[0].supplier : "",
								get_query: () => {
									return {
										filters: [
											[
												"Supplier",
												"name",
												"in",
												frm.doc.suppliers.map((row) => {
													return row.supplier;
												}),
											],
										],
									};
								},
							},
							{
								fieldtype: "Section Break",
								label: "Print Settings",
								fieldname: "print_settings",
								collapsible: 1,
							},
							{
								fieldtype: "Link",
								label: "Print Format",
								fieldname: "print_format",
								options: "Print Format",
								placeholder: "Standard",
								get_query: () => {
									return {
										filters: {
											doc_type: "Request for Quotation",
										},
									};
								},
							},
							{
								fieldtype: "Link",
								label: "Language",
								fieldname: "language",
								options: "Language",
								default: frappe.boot.lang,
							},
							{
								fieldtype: "Link",
								label: "Letter Head",
								fieldname: "letter_head",
								options: "Letter Head",
								default: frm.doc.letter_head,
							},
						],
						(data) => {
							var w = window.open(
								frappe.urllib.get_full_url(
									"/api/method/erpnext.buying.doctype.request_for_quotation.request_for_quotation.get_pdf?" +
									new URLSearchParams({
										name: frm.doc.name,
										supplier: data.supplier,
										print_format: data.print_format || "Standard",
										language: data.language || frappe.boot.lang,
										letterhead: data.letter_head || frm.doc.letter_head || "",
									}).toString()
								)
							);
							if (!w) {
								frappe.msgprint(__("Please enable pop-ups"));
								return;
							}
						},
						"Download PDF for Supplier",
						"Download"
					);
				},
				__("Tools")
			);

			frm.page.set_inner_btn_group_as_primary(__("Create"));
		}
	},

	make_supplier_quotation: function(frm) {
		var doc = frm.doc;
		var dialog = new frappe.ui.Dialog({
			title: __("Create Supplier Quotation"),
			fields: [
				{	"fieldtype": "Link",
					"label": __("Supplier"),
					"fieldname": "supplier",
					"options": 'Supplier',
					"reqd": 1,
					get_query: () => {
						return {
							filters: [
								["Supplier", "name", "in", frm.doc.suppliers.map((row) => {return row.supplier;})]
							]
						}
					}
				}
			],
			primary_action_label: __("Create"),
			primary_action: (args) => {
				if(!args) return;
				dialog.hide();

				return frappe.call({
					type: "GET",
					method: "erpnext.buying.doctype.request_for_quotation.request_for_quotation.make_supplier_quotation_from_rfq",
					args: {
						"source_name": doc.name,
						"for_supplier": args.supplier
					},
					freeze: true,
					callback: function(r) {
						if(!r.exc) {
							var doc = frappe.model.sync(r.message);
							frappe.set_route("Form", r.message.doctype, r.message.name);
						}
					}
				});
			}
		});

		dialog.show()
	},

	schedule_date(frm) {
		if(frm.doc.schedule_date){
			frm.doc.items.forEach((item) => {
				item.schedule_date = frm.doc.schedule_date;
			})
		}
		refresh_field("items");
	},
	preview: (frm) => {
		let dialog = new frappe.ui.Dialog({
			title: __('Preview Email'),
			fields: [
				{
					label: __('Supplier'),
					fieldtype: 'Select',
					fieldname: 'supplier',
					options: frm.doc.suppliers.map(row => row.supplier),
					reqd: 1
				},
				{
					fieldtype: 'Column Break',
					fieldname: 'col_break_1',
				},
				{
					label: __('Subject'),
					fieldtype: 'Data',
					fieldname: 'subject',
					read_only: 1,
					depends_on: 'subject'
				},
				{
					fieldtype: 'Section Break',
					fieldname: 'sec_break_1',
					hide_border: 1
				},
				{
					label: __('Email'),
					fieldtype: 'HTML',
					fieldname: 'email_preview'
				},
				{
					fieldtype: 'Section Break',
					fieldname: 'sec_break_2'
				},
				{
					label: __('Note'),
					fieldtype: 'HTML',
					fieldname: 'note'
				}
			]
		});

		dialog.fields_dict["supplier"].df.onchange = () => {
			frm.call("get_supplier_email_preview", {
				supplier: dialog.get_value("supplier"),
			}).then(({ message }) => {
				dialog.fields_dict.email_preview.$wrapper.empty();
				dialog.fields_dict.email_preview.$wrapper.append(
					message.message
				);
				dialog.set_value("subject", message.subject);
			});
		};

		dialog.fields_dict.note.$wrapper.append(`<p class="small text-muted">This is a preview of the email to be sent. A PDF of the document will
			automatically be attached with the email.</p>`);

		dialog.show();
	}
})
frappe.ui.form.on("Request for Quotation Item", {
	items_add(frm, cdt, cdn) {
		if (frm.doc.schedule_date) {
			frappe.model.set_value(cdt, cdn, 'schedule_date', frm.doc.schedule_date);
		}
	}
});
frappe.ui.form.on("Request for Quotation Supplier",{
	supplier: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn]
		frappe.call({
			method:"erpnext.accounts.party.get_party_details",
			args:{
				party: d.supplier,
				party_type: 'Supplier'
			},
			callback: function(r){
				if(r.message){
					frappe.model.set_value(cdt, cdn, 'contact', r.message.contact_person)
					frappe.model.set_value(cdt, cdn, 'email_id', r.message.contact_email)
				}
			}
		})
	},

})