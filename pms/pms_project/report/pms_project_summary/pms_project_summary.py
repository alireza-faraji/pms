# Copyright (c) 2024, Core Initiative and contributors
# For license information, please see license.txt

# import frappe


from collections import OrderedDict

import frappe
from frappe import _, _dict
from frappe.utils import cstr, getdate

def execute(filters=None):
	if not filters:
		columns, data = [], []
	columns = get_columns(filters)
	data = get_result(filters)
	return columns, data

def get_result(filters):

	entries = get_entries(filters)

	data = get_total(filters,entries)

	result = get_result_as_list(data, filters)

	return result

def get_entries(filters):
	select_fields = """`tabHMS Folio Transaction`.owner,`tabHMS Folio Transaction`.audit_date,`tabHMS Folio Transaction`.modified_by,`tabHMS Folio Transaction`.transaction_type, `tabHMS Folio Transaction`.amount, `tabHMS Folio Transaction`.parent,`tabHMS Folio`.customer_id """
	#select_fields = """owner,audit_date"""

	# if filters.get("show_remarks"):
	# 	select_fields += """,remarks"""

	order_by_statement = "order by `tabHMS Folio Transaction`.owner,`tabHMS Folio Transaction`.audit_date"


		
	entries = frappe.db.sql(
		"""
		select
			{select_fields}
		from `tabHMS Folio Transaction` inner join `tabHMS Folio` on `tabHMS Folio Transaction`.parent=`tabHMS Folio`.name
		where {conditions}
		{order_by_statement}
	""".format(
			select_fields=select_fields,
			conditions=get_conditions(filters),
			order_by_statement=order_by_statement
		),
		filters,
		as_dict=1,
	)

	return entries


def get_total(filters,entries):
	return entries


def get_conditions(filters):
	conditions = []
	conditions.append("`tabHMS Folio Transaction`.transaction_type = 'Payment'")
	conditions.append("is_void = 0")

	if filters.get("from_date"):
	 	conditions.append(" `tabHMS Folio Transaction`.audit_date >= %(from_date)s")

	if filters.get("to_date"):
	 	conditions.append(" `tabHMS Folio Transaction`.audit_date <= %(to_date)s")
	
	if filters.get("user"):
	 	conditions.append(" `tabHMS Folio Transaction`.owner = %(user)s")

	
	return "{}".format(" and ".join(conditions)) if conditions else "True"

def get_result_as_list(data, filters):
	 
	for d in data:
		print(d)
	return data

def get_columns(filters):
	color = "yellow"
	columns = []
	# [{"label": _("Folio"), "fieldname": "parent", "fieldtype": "Link","options":"HMS Folio", "width": 150},
	# {"label": _("Customer"), "fieldname": "customer_id", "fieldtype": "Link","options":"Customer", "width": 200},
	# ]
	department=filters.get("department")
	items=[
		{"name":"aaa","department":"Planning","title_ar":"نوع الاستثمار","lable":"Investment type","color":"red","width":"0","type":"Data"},
		{"name":"aaa","department":"Planning","lable_ar":"الباب","lable":"Unit","color":"red","width":"0","type":"Data"},
		{"name":"aaa","department":"Planning","lable_ar":"القسم","lable":"Section","color":"red","width":"0","type":"Data"},
		{"name":"aaa","department":"Planning","lable_ar":"الفصل","lable":"chapter","color":"red","width":"0","type":"Data"},
		{"name":"aaa","department":"Planning","lable_ar":"المادة","lable":"Subject","color":"red","width":"0","type":"Data"},
		{"name":"aaa","department":"Planning","lable_ar":"النوع","lable":"Type","color":"red","width":"0","type":"Data"},
		{"name":"aaa","department":"Planning","lable_ar":"تسلسل","lable":"sequence","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Planning","lable_ar":"اسم المشروع","lable":"Project Name","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Planning","lable_ar":"الكلفة الكلية(المصادقة)","lable":"Total cost (Approved)","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Planning","lable_ar":"القطاع","lable":"Sector","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Planning","lable_ar":"الوزارة","lable":"Ministry","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Government Contracts","lable_ar":"الموقع","lable":"Location","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Government Contracts","lable_ar":"اسم الشركة","lable":"Company Name","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Government Contracts","lable_ar":"رقم المناقصة","lable":"Bid Number","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Government Contracts","lable_ar":"كلفة الاحالة","lable":"Bid cost","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Planning","lable_ar":"مبلغ الاحتياط","lable":"Reserve amount","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Planning","lable_ar":"مبلغ الاشراف والمراقبة","lable":"The amount of supervision and monitoring","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Planning","lable_ar":"الكلفة الكلية للاحالة","lable":"Total cost of Bid","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Government Contracts","lable_ar":"مدة العقد","lable":"Duration of the contract","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Project Management","lable_ar":"تاريخ مباشرة","lable":"Date of start","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Planning","lable_ar":"تاريخ الانجاز التعاقدي","lable":"Contractual completion date","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Financial","lable_ar":"المصروف التراكمي","lable":"Total Cost","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Planning","lable_ar":"التخصيص","lable":"Allocation","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Planning","lable_ar":"الملاحظات","lable":"Notes","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Project Management","lable_ar":"موقف المشروع","lable":"Project Status","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Planning","lable_ar":"سنة الادراج","lable":"Year of listing","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Project Management","lable_ar":"تاريخ انجاز المشروع","lable":"Project completion date","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Financial","lable_ar":"المصروف من الاحتياط","lable":"expenditure from reserve","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Financial","lable_ar":"المصروف من الاشراف والمراقبة","lable":"Expenditure from supervision and control","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Financial","lable_ar":"المصروف السنوي","lable":"Annual expense","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Government Contracts","lable_ar":"رقم الإحالة","lable":"Bid number","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Government Contracts","lable_ar":"تاريخ الإحالة","lable":"Bid date","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Government Contracts","lable_ar":"تاريخ توقيع العقد","lable":"Date of contract signature ","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Project Management","lable_ar":"فترة التوقف","lable":"Downtime","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Project Management","lable_ar":"رقم وتاريخ فترة التوقف","lable":"Number and date of the suspension period","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Government Contracts","lable_ar":"رقم وتاريخ ملحق العقد","lable":"Number and date of the contract addendum","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Government Contracts","lable_ar":"مبلغ الإضافة لملحق العقد","lable":"The amount of the addition to the contract addendum","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Government Contracts","lable_ar":"مبلغ الحذف لملحق العقد","lable":"The deletion amount for the contract addendum","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Government Contracts","lable_ar":"المبلغ الكلي لملحق العقد","lable":"The total amount of the contract addendum","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Government Contracts","lable_ar":"المدد الإضافية لملحق العقد","lable":"Additional periods for the contract addendum","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Planning","lable_ar":"تنزيل تخصيص","lable":"Download Allocation","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Planning","lable_ar":"إضافة تخصيص","lable":"Add Allocation","color":"yellow","width":"0","type":"Data"},
		{"name":"aaa","department":"Planning","lable_ar":"تخصيص بعد المناقلة","lable":"Allocation after transfer","color":"yellow","width":"0","type":"Data"}
	]

	for item in items:
		if "Planning" in department:
			color = "#4ef575"
		if "Financial" in department:
			color = "#f54e4e"
		if "Project Management" in department:
			color = "#f59c4e"
		if "Government Contracts" in department:
			color = "#4e91f5"
			
		if item["department"] in department or not department:
			columns.append(

				{"label":"<span style='display: block;background-color:"+item["color"]+";color:red!important;font-weight:bold'>"+item["lable"]+"</span>", "fieldname": "amount", "fieldtype": item["type"]},
			)
	
	

	# department=filters.get("department")
	# if "Planning" in department:
	# 	columns.append(
	# 	{
	# 		"label": _("Audit Date"),
	# 		"fieldname": "audit_date",
	# 		"fieldtype": "DateTime",
	# 		"width": 140,
	# 	}
	# 	)
	# if "Government Contracts" in department:
	# 	columns.append(
	# 	{"label": _("Amount"), "fieldname": "amount", "fieldtype": "Float", "width": 150}
	# 	)
	
	return columns
