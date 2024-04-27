// Copyright (c) 2024, Core Initiative and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["PMS Project Summary"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_days(frappe.datetime.get_today(), -1),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"user",
			"label": __("User"),
			"fieldtype": "Link",
			"default": "",
			"options":"User",
			"reqd": 0,
			"width": "60px"
		},
        {
			"fieldname":"department",
			"label": __("Department"),
			"fieldtype": "MultiSelectList",
			"width": 100,
			get_data: function(txt) {
				let status = ["Planning", "Government Contracts", "Project Management", "Financial"]
				let options = []
				for (let option of status){
					options.push({
						"value": option,
						"label": __(option),
						"description": ""
					})
				}
				return options
			}
		},
	]
    ,
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
    //    if (columnDef.id != "Customer" && columnDef.id != "Payment Date" && dataContext["Rental Payment"] < 100) {
    //            value = "<span style='color:red!important;font-weight:bold'>" + value + "</span>";
    //     }
    //    if (columnDef.id != "Customer" && columnDef.id != "Payment Date" && dataContext["Rental Payment"] > 100) {
               value = "aaaaa";
//        }
        return value;
    }
};

//     if (data && data.bold) {
//         value = value.bold();

//     }
//     return value;
// },
 
   