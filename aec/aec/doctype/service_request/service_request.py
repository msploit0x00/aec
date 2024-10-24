# Copyright (c) 2024, ds and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.accounts.utils import get_balance_on
from datetime import datetime
from frappe.utils import (
	add_days,
	cint,
	create_batch,
	cstr,
	flt,
	formatdate,
	get_datetime,
	get_number_format_info,
	getdate,
	now,
	nowdate,
)

class ServiceRequest(Document):
	def validate(self):
		self.validate_customer()
		self.get_member_committees()
		self.allow_outstanding()
		self.show_export_volumes()
		self.allow_repeated()
		self.get_service_items()
		self.prod_member()
		self.get_service_default_price_list()

	def before_save(self):
		# self.calc_total()
		self.prod_count()
		self.apply_price_list_rate()

	# def after_save(self):
	# 	self.calc_total()


	def validate_customer(self):
		service = self.select_service

		service_data = frappe.get_doc("Service Generator", service)

		membership_status = self.membership_status
		# allowed_status = [service_data.request,service_data.active,service_data.inactive,service_data.suspended,service_data.data_completion]
		
		status_mapping = {
			"Requested": service_data.request,
        	"Active": service_data.active,
        	"Inactive": service_data.inactive,
        	"Suspended": service_data.suspended,
        	"Data completion": service_data.data_completion
    	}

		if membership_status in status_mapping and status_mapping[membership_status]:
			print("Allowed")
		else:
			frappe.throw(f"This Service is not Allowed For this Member")


	def get_member_committees(self):
		member = self.member
		service = self.select_service

		service_data = frappe.get_doc("Service Generator", service)

		if(service_data.show_committees == 1):
			comm =frappe.get_all("Committees you would like to join", 
				  filters={'parenttype':'Customer','parent': member},
				  fields=['committees','salutation'])

			self.set('committees_member_join',[])

			for row in comm:
				self.append('committees_member_join',{
				'committees': row.committees,
				'salutation': row.salutation
			})
		


	def allow_outstanding(self):
		service = self.select_service

		outstanding = self.member_outstanding
		service_data = frappe.get_doc("Service Generator", service)

		# if(outstanding != 0.00):
		if(service_data.allow_outstanding == 1 ):
			print("Allowed")
		
		else:
			frappe.throw("This Service Not Allowed Members Outstanding")



	def show_export_volumes(self):
		service = self.select_service
		member = self.member
		service_data = frappe.get_doc("Service Generator", service)

		if(service_data.show_export_volume == 1):

			volume = frappe.get_all("Volume Of Member Exports for Three Years", 
						   filters={'parenttype': 'Customer', 'parent': member},
						   fields=['season','season_name','value','total_amount_in_usd','quantity_in_tons'])

			self.set('member_export_volume',[])

			for row in volume:
				self.append("member_export_volume",{
					'season': row.season,
					'season_name':row.season_name,
					'value': row.value,
					'total_amount_in_usd': row.total_amount_in_usd,
					'quantity_in_tons': row.quantity_in_tons
				})
		
	
	def get_service_items(self):
		service = self.select_service

		service_data = frappe.get_doc("Service Generator", service)

		items_data = service_data.service_items

		self.set("items", [])

		for row in items_data:

			self.append('items',{
				'item_code': row.item,
				'item_name': row.item,
				'qty': 1.0,
				# 'rate': row.pricing,
				# 'amount': 1.0 * row.pricing
			})
		
	
	def allow_repeated(self):
		member = self.member
		service = self.select_service
		current_year = datetime.now().year

		service_data = frappe.get_doc("Service Generator", service)

		all_invoices = frappe.get_all('Sales Invoice', 
								filters={'posting_date': str(current_year),'customer': member,'custom_service_group': service, 'docstatus': 1})

		if(service_data.repeated_service):
			if len(all_invoices) != service_data.repeated_how_many:
				print("Allowed")
			else:
				frappe.throw("This Member is Not Allowed To take this service Again")


	def calc_total(self):
		total = 0.0
		for item in self.items:
			total += item.amount
		
		self.total_amount = total

	##TEST
	def prod_member(self):
		service = self.select_service

		service_data = frappe.get_doc("Service Generator", service).as_dict()

		member_category = self.member_category

		service_items = service_data.get("service_items")

		if service == 'عضوية لجنة سلعية':
			for items in service_items:
				if member_category == items.category:
					self.set("items",[])
					self.append('items',{
				'item_code': items.item,
				'item_name': items.item,
				'qty': 1.0,
				'rate': items.pricing,
				'amount': 1.0 * items.pricing
			})

		######################################TESTING######################
	def prod_count(self):
		count = frappe.db.count("Committees you would like to join",
						  filters={'parenttype': 'Customer','parent':self.member,'salutation':'عضوية لجنة سلعية'})
		
		print(f"this is the count {count}")
		return count

	def wakeel_count(self):
		count = frappe.db.count("Committees you would like to join",
						  filters={'parenttype': 'Customer','parent':self.member,'salutation':'عضوية وكيل لجنة'})
		
		print(f"this is the count {count}")
		return count		


	def ra2ees_count(self):
		count = frappe.db.count("Committees you would like to join",
						  filters={'parenttype': 'Customer','parent':self.member,'salutation':'عضوية رئيس لجنة'})
		
		print(f"this is the count {count}")
		return count			


	def serv_count(self):
		count = frappe.db.count("Committees you would like to join",
						  filters={'parenttype': 'Customer','parent':self.member,'salutation':'عضوية لجنة خدمية'})
		
		print(f"this is the count {count}")
		return count	



	def get_service_default_price_list(self):
		service = self.select_service
		if service:
			service_data = frappe.get_doc("Service Generator", service)
			if service_data:
				price_list = service_data.service_price_list

				for row in price_list:
					if row.is_default == 1:
						self.price_list = row.price_list
					# else:
					# 	frappe.throw("This Service Doesn't have default price list, please set default one")




	def apply_price_list_rate(self):
		if self.price_list:
			items = self.items

			if len(items) > 0:
				for row in items:
					item_price = frappe.get_list("Item Price", filters={'price_list': self.price_list, 'item_code': row.item_code})
					
					item_price_data = frappe.get_doc("Item Price", item_price)
					
					
					print(f"AAAAAAAAAAAAAA {item_price}")
					if item_price_data:
						price_list_rate = item_price_data.price_list_rate

						row.rate = price_list_rate
						row.base_rate = price_list_rate
						row.base_amount= row.qty * price_list_rate
						row.amount = row.qty * price_list_rate
			self.calc_total()





@frappe.whitelist(allow_guest=True)
def create_sales_invoice(doc_name):
	try:
		request_doc = frappe.get_doc("Service Request", doc_name)
		date = request_doc.date
		service = request_doc.select_service
		year = request_doc.year
		tax_id = request_doc.tax_id
		custom_invoice_type = 'Members'
		membership_status = request_doc.membership_status
		volume_of_exports = request_doc.volume_of_exports
		member_category = request_doc.member_category
		payment_status = request_doc.payment_status
		member_outstanding = request_doc.member_outstanding
		member = request_doc.member

		committees = frappe.get_all("Committees customer join", 
							  filters={'parent': doc_name},
							  fields=['committees','salutation'])
		
		vol = frappe.get_all("log Sales Invoice", 
					   filters={'parent': doc_name},
					   fields=['season','value','season_name','total_amount_in_usd','quantity_in_tons'])
		

		history = frappe.get_all("Member History", 
						   filters={'parent': doc_name},
						   fields=['*'])
		

		items = frappe.get_all("Service Request Item",
						 filters={'parent': doc_name},
						 fields=['*'])



		new_invoice = frappe.get_doc({
			'doctype': 'Sales Invoice',
			'customer': member,
			'posting_date': date,
			'custom_service_group': service,
			'custom_invoice_type': 'Members',
			'custom_customer_outstanding_balance': member_outstanding,
			'custom_customer_group': member_category,
			'custom_volume_of_exports': volume_of_exports,
			'custom_customer_membership_status': membership_status,
			'custom_membership_status': payment_status,
			'is_pos': 1,

		})


		if len(committees) > 0:
			for comm in committees:
				new_invoice.append('custom_committees_customer_joined_',{
				'committees': comm['committees'],
				'salutation': comm['salutation']
			})

		if len(vol) > 0:
			for volumes in vol:
				new_invoice.append('custom_log',{
				'season': volumes['season'],
				'value': volumes['value'],
				'season_name': volumes['season_name'],
				'total_amount_in_usd': volumes['total_amount_in_usd'],
				'quantity_in_tons': volumes['quantity_in_tons']
			})
		
		if len(history) > 0:
			for his in history:
				new_invoice.append('custom_member_history',{
					'year': his['year'],
					'season_name': his['season_name'],
					'volume_of_exports': his['volume_of_exports'],
					'member_categories': his['member_categories'],
					'paid_amount': his['paid_amount'],
					'outstanding_amount': his['outstanding_amount'],
					'sales_invoice_ref': his['sales_invoice_ref']
				})
		
		if len(items) > 0:
			for item in items:
				new_invoice.append('items',{
					'item_code': item['item_code'],
					'item_name': item['item_name'],
					'qty': item['qty'],
					'rate': item['rate'],
					'amount': item['amount'],
				})

		new_invoice.append('payments',{
			'mode_of_payment': 'Cash',
			'amount': new_invoice.total
		})

		new_invoice.insert(ignore_permissions=True)


		return new_invoice.name
	
	except Exception as e:
		frappe.throw("Error in Creating Sales Invoice, Please Check all data in request")












@frappe.whitelist()
def volume_of_member_exports_three_years(tax_ids):
    # Get the last 3 distinct years starting from the previous year (current year - 1)
    years = frappe.db.sql("""
        SELECT DISTINCT YEAR(`year`) 
        FROM `tabVolume Of Member Exports`
        WHERE YEAR(`year`) <= YEAR(CURDATE()) - 1
        ORDER BY YEAR(`year`) DESC
        LIMIT 3
    """, as_list=1)
    
    # Flatten the list of years and ensure it's not empty
    years = [y[0] for y in years if y[0] is not None]

    if not years:
        # Return an empty result if no valid years are found
        return []

    # Fetch export data for the selected years
    data = frappe.db.sql("""
        SELECT
            `tax__number` AS `tax_id`,
            `season__name` AS `season_name`,
            `season` AS `season`,
            SUM(`total_amount_in_egp`) AS `total`,
            SUM(`total_amount_in_usd`) AS `total_amount_in_usd`,
            SUM(`quantity_in_tons`) AS `quantity_in_tons`
        FROM
            `tabVolume Of Member Exports`
        WHERE 
            YEAR(`year`) IN (%s)
            AND tax__number IN (%s)
        GROUP BY
            `tax__number`, `season__name`, `season`
        """ % (','.join([str(year) for year in years]), ','.join(['%s'] * len(tax_ids))),
        tuple(tax_ids),
        as_dict=1
    )
    
    return data


# def get_memebr_exports(tax_id):
# 	current = nowdate().year






