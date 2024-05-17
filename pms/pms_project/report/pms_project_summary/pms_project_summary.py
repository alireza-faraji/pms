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

	entries = get_projects(filters)

	data = get_total(filters,entries)

	result = get_result_as_list(data, filters)

	return result

def get_projects(filters):
	select_fields = """`tabPMS Main Project`.`part`,`tabPMS Main Project`.`investment_type`,`tabPMS Main Project`.`section`,`tabPMS Main Project`.`chapter`,`tabPMS Main Project`.`item`,`tabPMS Main Project`.`type`,`tabPMS Main Project`.`name`,`tabPMS Main Project`.`project_name`,`tabPMS Main Project`.`total_cost_approved`"""
	#select_fields = """owner,audit_date"""

	# if filters.get("show_remarks"):
	# 	select_fields += """,remarks"""

	order_by_statement ="" #"order by `tabHMS Folio Transaction`.owner,`tabHMS Folio Transaction`.audit_date"


		
	entries = frappe.db.sql(
		"""
		select
			{select_fields}
		from `tabPMS Main Project` 
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
def get_sub_projects(filters,main_project):
	select_fields = """`tabProject`.`custom_main_project`,`tabProject`.`custom_sector`,`tabProject`.`custom_ministry`,`tabProject`.`custom_location`,`tabProject`.`custom_company_name`,`tabProject`.`custom_bid_number`,`tabProject`.`custom_bid_cost`,`tabProject`.`custom_emergency_cost`,`tabProject`.`custom_supervision_cost`,`tabProject`.`custom_total_amount`,`tabProject`.`custom_contract_period`,`tabProject`.`custom_start_date`,`tabProject`.`custom_end_date`"""
	#select_fields = """owner,audit_date"""

	# if filters.get("show_remarks"):
	# 	select_fields += """,remarks"""

	order_by_statement ="" #"order by `tabHMS Folio Transaction`.owner,`tabHMS Folio Transaction`.audit_date"


		
	entries = frappe.db.sql(
		"""
		select
			{select_fields}
		from `tabProject` 
		where {conditions}
		{order_by_statement}
	""".format(
			select_fields=select_fields,
			conditions=get_sub_project_conditions(filters,main_project),
			order_by_statement=order_by_statement
		),
		filters,
		as_dict=1,
	)

	return entries

def get_total(filters,entries):
	all_entries=[]
	for item in entries:
		item["doc_type"]="main_project"
		all_entries.append(item)
		sub_projects=get_sub_projects(filters,item["name"])
		for sub_item in sub_projects:
			sub_item["doc_type"]="sub_project"
			all_entries.append(sub_item)
	#print(all_entries)
	return all_entries


def get_conditions(filters):
	conditions = []
	#conditions.append("`tabPMS Main Project`.name <> ''")
	#conditions.append("is_void = 0")

	# if filters.get("from_date"):
	#  	conditions.append(" `tabHMS Folio Transaction`.audit_date >= %(from_date)s")

	# if filters.get("to_date"):
	#  	conditions.append(" `tabHMS Folio Transaction`.audit_date <= %(to_date)s")
	
	# if filters.get("user"):
	#  	conditions.append(" `tabHMS Folio Transaction`.owner = %(user)s")

	
	return "{}".format(" and ".join(conditions)) if conditions else "True"
def get_sub_project_conditions(filters,main_project):
	conditions = []
	conditions.append(f"custom_main_project = '{main_project}'")
	#conditions.append("is_void = 0")

	# if filters.get("from_date"):
	#  	conditions.append(" `tabHMS Folio Transaction`.audit_date >= %(from_date)s")

	# if filters.get("to_date"):
	#  	conditions.append(" `tabHMS Folio Transaction`.audit_date <= %(to_date)s")
	
	# if filters.get("user"):
	#  	conditions.append(" `tabHMS Folio Transaction`.owner = %(user)s")

	
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
		{"fieldname":"project_name","department":"Planning","lable_ar":"اسم المشروع","lable":"Project Name","color":"#09ce06","width":"0","type":"Data"},
		{"fieldname":"part","department":"Planning","lable_ar":"الباب","lable":"Unit","color":"#09ce06","width":"0","type":"Data"},
		{"fieldname":"investment_type","department":"Planning","title_ar":"نوع الاستثمار","lable":"Investment type","color":"#09ce06","width":"0","type":"Data"},
		{"fieldname":"section","department":"Planning","lable_ar":"القسم","lable":"Section","color":"#09ce06","width":"0","type":"Data"},
		{"fieldname":"chapter","department":"Planning","lable_ar":"الفصل","lable":"chapter","color":"#09ce06","width":"0","type":"Data"},
		{"fieldname":"item","department":"Planning","lable_ar":"المادة","lable":"Subject","color":"#09ce06","width":"0","type":"Data"},
		{"fieldname":"type","department":"Planning","lable_ar":"النوع","lable":"Type","color":"#09ce06","width":"0","type":"Data"},
		{"fieldname":"name","department":"Planning","lable_ar":"تسلسل","lable":"sequence","color":"#09ce06","width":"0","type":"Data"},
		{"fieldname":"total_cost_approved","department":"Planning","lable_ar":"الكلفة الكلية(المصادقة)","lable":"Total cost (Approved)","color":"#09ce06","width":"0","type":"Data"},
		
		{"fieldname":"custom_sector","department":"Planning","lable_ar":"القطاع","lable":"Sector","color":"#09ce06","width":"0","type":"Data"},
		{"fieldname":"custom_ministry","department":"Planning","lable_ar":"الوزارة","lable":"Ministry","color":"#09ce06","width":"0","type":"Data"},
		{"fieldname":"custom_location","department":"Government Contracts","lable_ar":"الموقع","lable":"Location","color":"#00a7ff","width":"0","type":"Data"},
		{"fieldname":"custom_company_name","department":"Government Contracts","lable_ar":"اسم الشركة","lable":"Company Name","color":"#00a7ff","width":"0","type":"Data"},
		{"fieldname":"custom_bid_number","department":"Government Contracts","lable_ar":"رقم المناقصة","lable":"Bid Number","color":"#00a7ff","width":"0","type":"Data"},
		{"fieldname":"custom_bid_cost","department":"Government Contracts","lable_ar":"كلفة الاحالة","lable":"Bid cost","color":"#00a7ff","width":"0","type":"Data"},
		{"fieldname":"custom_emergency_cost","department":"Planning","lable_ar":"مبلغ الاحتياط","lable":"Reserve amount","color":"#09ce06","width":"0","type":"Data"},
		{"fieldname":"custom_supervision_cost","department":"Planning","lable_ar":"مبلغ الاشراف والمراقبة","lable":"The amount of supervision and monitoring","color":"#09ce06","width":"0","type":"Data"},
		{"fieldname":"custom_total_amount","department":"Planning","lable_ar":"الكلفة الكلية للاحالة","lable":"Total cost of Bid","color":"#09ce06","width":"0","type":"Data"},
		{"fieldname":"custom_contract_period","department":"Government Contracts","lable_ar":"مدة العقد","lable":"Duration of the contract","color":"#00a7ff","width":"0","type":"Data"},
		{"fieldname":"custom_start_date","department":"Project Management","lable_ar":"تاريخ مباشرة","lable":"Date of start","color":"#ff9300","width":"0","type":"Data"},
		{"fieldname":"custom_end_date","department":"Planning","lable_ar":"تاريخ الانجاز التعاقدي","lable":"Contractual completion date","color":"#09ce06","width":"0","type":"Data"},
		
		
		
		# {"name":"aaa","department":"Financial","lable_ar":"المصروف التراكمي","lable":"Total Cost","color":"yellow","width":"0","type":"Data"},
		# {"name":"aaa","department":"Planning","lable_ar":"التخصيص","lable":"Allocation","color":"yellow","width":"0","type":"Data"},
		# {"name":"aaa","department":"Planning","lable_ar":"الملاحظات","lable":"Notes","color":"yellow","width":"0","type":"Data"},
		# {"name":"aaa","department":"Project Management","lable_ar":"موقف المشروع","lable":"Project Status","color":"yellow","width":"0","type":"Data"},
		# {"name":"aaa","department":"Planning","lable_ar":"سنة الادراج","lable":"Year of listing","color":"yellow","width":"0","type":"Data"},
		# {"name":"aaa","department":"Project Management","lable_ar":"تاريخ انجاز المشروع","lable":"Project completion date","color":"yellow","width":"0","type":"Data"},
		# {"name":"aaa","department":"Financial","lable_ar":"المصروف من الاحتياط","lable":"expenditure from reserve","color":"yellow","width":"0","type":"Data"},
		# {"name":"aaa","department":"Financial","lable_ar":"المصروف من الاشراف والمراقبة","lable":"Expenditure from supervision and control","color":"yellow","width":"0","type":"Data"},
		# {"name":"aaa","department":"Financial","lable_ar":"المصروف السنوي","lable":"Annual expense","color":"yellow","width":"0","type":"Data"},
		# {"name":"aaa","department":"Government Contracts","lable_ar":"رقم الإحالة","lable":"Bid number","color":"yellow","width":"0","type":"Data"},
		# {"name":"aaa","department":"Government Contracts","lable_ar":"تاريخ الإحالة","lable":"Bid date","color":"yellow","width":"0","type":"Data"},
		# {"name":"aaa","department":"Government Contracts","lable_ar":"تاريخ توقيع العقد","lable":"Date of contract signature ","color":"yellow","width":"0","type":"Data"},
		# {"name":"aaa","department":"Project Management","lable_ar":"فترة التوقف","lable":"Downtime","color":"yellow","width":"0","type":"Data"},
		# {"name":"aaa","department":"Project Management","lable_ar":"رقم وتاريخ فترة التوقف","lable":"Number and date of the suspension period","color":"yellow","width":"0","type":"Data"},
		# {"name":"aaa","department":"Government Contracts","lable_ar":"رقم وتاريخ ملحق العقد","lable":"Number and date of the contract addendum","color":"yellow","width":"0","type":"Data"},
		# {"name":"aaa","department":"Government Contracts","lable_ar":"مبلغ الإضافة لملحق العقد","lable":"The amount of the addition to the contract addendum","color":"yellow","width":"0","type":"Data"},
		# {"name":"aaa","department":"Government Contracts","lable_ar":"مبلغ الحذف لملحق العقد","lable":"The deletion amount for the contract addendum","color":"yellow","width":"0","type":"Data"},
		# {"name":"aaa","department":"Government Contracts","lable_ar":"المبلغ الكلي لملحق العقد","lable":"The total amount of the contract addendum","color":"yellow","width":"0","type":"Data"},
		# {"name":"aaa","department":"Government Contracts","lable_ar":"المدد الإضافية لملحق العقد","lable":"Additional periods for the contract addendum","color":"yellow","width":"0","type":"Data"},
		# {"name":"aaa","department":"Planning","lable_ar":"تنزيل تخصيص","lable":"Download Allocation","color":"yellow","width":"0","type":"Data"},
		# {"name":"aaa","department":"Planning","lable_ar":"إضافة تخصيص","lable":"Add Allocation","color":"yellow","width":"0","type":"Data"},
		# {"name":"aaa","department":"Planning","lable_ar":"تخصيص بعد المناقلة","lable":"Allocation after transfer","color":"yellow","width":"0","type":"Data"}
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

				{"label":"<span style='display: block;background-color:"+item["color"]+";color:black!important;font-weight:bold'>"+item["lable"]+"</span>", "fieldname": item["fieldname"], "fieldtype": item["type"]},
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
