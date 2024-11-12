# Copyright (c) 2024, ds and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.accounts.utils import get_balance_on
from datetime import datetime
import time
from frappe import _
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
from barcode_aec.update_mem_vol import get_customer_group

class ServiceRequest(Document):
	def validate(self):
		self.validate_customer() ##
		self.get_member_committees() ##
		self.allow_outstanding() ##
		self.show_export_volumes() ##
		self.allow_repeated() ##
		# self.get_service_items() ##
		self.prod_member()
		self.get_service_default_price_list()
		# self.get_service_print_format() 

	def before_save(self):
		# self.calc_total()
		self.prod_count()
		self.get_service_items()
		# self.calc_total()
		self.apply_price_list_rate()
		self.get_member_history()
		self.prepare_new_membership()
		# self.custom_prod_past_year()
		# self.perpare_new_membership2()
		self.get_income_account()
		self.get_last_serial_khetab()


	def after_save(self):
		pass
		# self.calc_total()
		# pass
		# self.get_income_account()
		# self.apply_price_list_rate()

		# self.calc_total()
		# self.calc_total()
		# self.get_service_items()
	# def on_update(self):
	# 	self.apply_price_list_rate()

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

			volume = frappe.get_all("Volume of Exports In Years", 
						   filters={'parenttype': 'Customer', 'parent': member},
						   order_by='year desc',
						   limit=3,
						   fields=['year','total_amount_in_usd','quantity_in_tons','total_amount_in_egp'])

			self.set('member_export_volume',[])

			for row in volume:
				self.append("member_export_volume",{
					'year': row.year,
					'total_amount_in_egp': row.total_amount_in_egp,
					'total_amount_in_usd': row.total_amount_in_usd,
					'quantity_in_tons': row.quantity_in_tons
				})
		
	
	def get_service_items(self):
		if self.select_service != 'تجديد العضوية':
			service = self.select_service

			service_data = frappe.get_doc("Service Generator", service)

			items_data = service_data.service_items
			current_items = {item.item_code: item for item in self.items}


			self.set("items", [])

			for row in items_data:
				existing_item = current_items.get(row.item)

				qty = existing_item.qty if existing_item else 1.0

				self.append('items',{
					'item_code': row.item,
					'item_name': row.item,
					'qty': qty,
					# 'rate': row.pricing,
					# 'amount': 1.0 * row.pricing
				})
		self.apply_price_list_rate()
		self.calc_total()

	
	def allow_repeated(self):
		member = self.member
		service = self.select_service
		current_year = datetime.now().year

		service_data = frappe.get_doc("Service Generator", service)

		all_invoices = frappe.get_all('Sales Invoice', 
								filters={'posting_date': str(current_year),'customer': member,'custom_service_group': service, 'docstatus': 1})

		if(service_data.repeated_service == 1):
			if len(all_invoices) != service_data.repeated_how_many:
				print("Allowed")
			else:
				frappe.throw("This Member is Not Allowed To take this service Again")


	def calc_total(self):
		total = 0.0
		if len(self.items) > 0:
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
		current_year = datetime.now().year
		if service and current_year == self.year:
			service_data = frappe.get_doc("Service Generator", service)
			if service_data:
				price_list = service_data.service_price_list

				for row in price_list:
					if row.is_default == 1:
						self.price_list = row.price_list
					# else:
					# 	frappe.throw("This Service Doesn't have default price list, please set default one")



	@frappe.whitelist()
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



	@frappe.whitelist()
	def get_member_history(self):
		service = self.select_service
		if service == 'تجديد العضوية':
			history = frappe.get_all("Sales Invoice",
							filters={'custom_service_group':'تجديد العضوية','customer': self.member,'status': ['in',['Unpaid','Overdue','Partly Paid','Paid']]},
							order_by="creation desc",
							fields=['year','paid_amount','name','custom_volume_of_exports','custom_customer_group','outstanding_amount','custom_service_group','status'])


			if len(history) > 0:
				self.set('member_history',[])

				for row in history:
					self.append("member_history",{
						'year': row.year,
						'paid_amount': row.paid_amount,
						'sales_invoice_ref': row.name,
						'member_categories': row.custom_customer_group,
						'volume_of_exports': row.custom_volume_of_exports,
						'outstanding_amount': row.outstanding_amount,
						'status': row.status
						# 'season_name': self.member_export_volume[0].season_name
					})
			
				

	def prepare_new_membership(self):
		if self.select_service == 'تجديد العضوية' and self.year == datetime.now().year:
			# Fetch list of dictionaries with 'salutation' for each committee
			member_comm = frappe.get_all(
				"Committees you would like to join",
				filters={'parenttype': 'Customer', 'parent': self.member},
				fields=['salutation']
			)

			self.set('items', [])			
			print("Fetched Committees:", member_comm)
			self.perpare_new_membership_prod()
			self.prep_wakeel()
			self.prep_ra2ees()
			self.prep_serv()

			found_item = False
			for comm in member_comm:
				print("Processing Committee:", comm)
				

###############################################################################################


			# found_item2 = False  # Flag to prevent duplicate appending

			# if not found_item2:  # Check if the item has already been added
			# 	# Assuming this block is inside a loop for member_comm or another iteration
			# 	if comm['salutation'] == 'عضوية رئيس لجنة' and not found_item2:
			# 		item_rate2 = frappe.get_all(
			# 			"Item Price",
			# 			filters={'price_list': self.price_list, 'item_code': 'عضوية رئيس لجنة'},
			# 			fields=['item_code', 'item_name', 'price_list_rate'],
			# 			limit=1
			# 		)

			# 		print(f"item rate 2 {item_rate2}")

			# 		count2 = self.ra2ees_count()

			# 		if item_rate2:
			# 			row2 = item_rate2[0]
			# 			self.append("items", {
			# 				'item_code': row2.get('item_code'),
			# 				'item_name': row2.get('item_name'),
			# 				'qty': count2,
			# 				'rate': row2.get('price_list_rate'),
			# 				'amount': count2 * row2.get("price_list_rate")
			# 			})

			# 			found_item2 = True  # Set flag to True after appending the item


##########################################################################################
			# added_membership = False
			# if not added_membership:  # Check the flag before processing any comms
			# 	for comm in member_comm:  # Assuming this loop is iterating over member_comm
			# 		if comm['salutation'] == 'عضوية لجنة خدمية' and not added_membership:
			# 			item_rate3 = frappe.get_all(
			# 				"Item Price",
			# 				filters={'price_list': self.price_list, 'item_code': 'عضوية لجنة خدمية'},
			# 				fields=['item_code', 'item_name', 'price_list_rate'],
			# 				limit=1
			# 			)

			# 			print(f"item rate 2 {item_rate3}")

			# 			count3 = self.serv_count()

			# 			if item_rate3:
			# 				row3 = item_rate3[0]

			# 				self.append("items", {
			# 					'item_code': row3.get('item_code'),
			# 					'item_name': row3.get('item_name'),
			# 					'qty': count3,
			# 					'rate': row3.get('price_list_rate'),
			# 					'amount': count3 * row3.get("price_list_rate")
			# 				})
			# 				added_membership = True  # Set the flag to True after appending the item
		self.calc_total()
					     
################################################################################################
			# added_membership2 = False  # Flag to prevent duplicate appending

			# # Check if the item has already been added for "عضوية وكيل لجنة"
			# if not added_membership2:  
			# 	if comm['salutation'] == 'عضوية وكيل لجنة':
			# 		item_rate4 = frappe.get_all(
			# 			"Item Price",
			# 			filters={'price_list': self.price_list, 'item_code': 'عضوية وكيل لجنة'},
			# 			fields=['item_code', 'item_name', 'price_list_rate'],
			# 			limit=1
			# 		)

			# 		print(f"item rate 4 {item_rate4}")

			# 		count4 = self.wakeel_count()

			# 		if item_rate4:
			# 			row4 = item_rate4[0]
			# 			self.append("items", {
			# 				'item_code': row4.get('item_code'),
			# 				'item_name': row4.get('item_name'),
			# 				'qty': count4,
			# 				'rate': row4.get('price_list_rate'),
			# 				'amount': count4 * row4.get("price_list_rate")
			# 			})
			# 			added_membership2 = True  # Set flag to True after appending the item


###########################################################################################################




	



	def perpare_new_membership_prod(self):
		if self.select_service == 'تجديد العضوية':
			# Retrieve the relevant committee memberships for the member
			member_comm = frappe.get_all(
				"Committees you would like to join",
				filters={'parenttype': 'Customer', 'parent': self.member},
				fields=['salutation']
			)

			# Fetch the service items from the selected service
			service_data = frappe.get_doc("Service Generator", self.select_service)
			service_items = service_data.service_items
			member_category = self.member_category

			item_added = False  # Flag to check if item has been appended already

			# Look for the specific item 'عضوية لجنة سلعية-4' once
			for comm in member_comm:
				if comm.salutation == 'عضوية لجنة سلعية' and not item_added:
					# Find the first matching item in service items
					for row in service_items:
						if self.member_category == row.category:
							# Prepare item details
							qty = self.prod_count()
							item_price = frappe.get_all(
								"Item Price",
								filters={'item_code': row.item, 'price_list': self.price_list},
								fields=['price_list_rate']
							)
							if item_price:
								item_code = row.item
								rate = item_price[0].price_list_rate if item_price else 0

								# Append the specific item and exit both loops immediately
								self.append('items', {
									'item_code': row.item,
									'item_name': row.item,
									'qty': qty,
									'rate': rate,
									'amount': rate * qty
								})
								item_added = True  # Set flag to True to prevent duplicate
								break  # Exit the inner loop once the item is appended
					break  # Exit the outer loop after the item has been added

	
	def prep_wakeel(self):
		member_comm = frappe.get_all(
				"Committees you would like to join",
				filters={'parenttype': 'Customer', 'parent': self.member},
				fields=['salutation']
			)
		added_membership2 = False  # Flag to prevent duplicate appending

		for comm in member_comm:# Check if the item has already been added for "عضوية وكيل لجنة"
			if not added_membership2:  
				if comm['salutation'] == 'عضوية وكيل لجنة':
					item_rate4 = frappe.get_all(
							"Item Price",
							filters={'price_list': self.price_list, 'item_code': 'عضوية وكيل لجنة'},
							fields=['item_code', 'item_name', 'price_list_rate'],
							limit=1
						)

					print(f"item rate 4 {item_rate4}")

					count4 = self.wakeel_count()

					if item_rate4:
						row4 = item_rate4[0]
						self.append("items", {
								'item_code': row4.get('item_code'),
								'item_name': row4.get('item_name'),
								'qty': count4,
								'rate': row4.get('price_list_rate'),
								'amount': count4 * row4.get("price_list_rate")
							})
						added_membership2 = True  # Set flag to True after appending the item


	def prep_ra2ees(self):
		member_comm = frappe.get_all(
				"Committees you would like to join",
				filters={'parenttype': 'Customer', 'parent': self.member},
				fields=['salutation']
			)
		added_membership2 = False  # Flag to prevent duplicate appending

		for comm in member_comm:# Check if the item has already been added for "عضوية وكيل لجنة"
			if not added_membership2:  
				if comm['salutation'] == 'عضوية رئيس لجنة':
					item_rate4 = frappe.get_all(
							"Item Price",
							filters={'price_list': self.price_list, 'item_code': 'عضوية رئيس لجنة'},
							fields=['item_code', 'item_name', 'price_list_rate'],
							limit=1
						)

					print(f"item rate 4 {item_rate4}")

					count4 = self.ra2ees_count()

					if item_rate4:
						row4 = item_rate4[0]
						self.append("items", {
								'item_code': row4.get('item_code'),
								'item_name': row4.get('item_name'),
								'qty': count4,
								'rate': row4.get('price_list_rate'),
								'amount': count4 * row4.get("price_list_rate")
							})
						added_membership2 = True  # Set flag to True after appending the item





	def prep_serv(self):
		member_comm = frappe.get_all(
				"Committees you would like to join",
				filters={'parenttype': 'Customer', 'parent': self.member},
				fields=['salutation']
			)
		added_membership2 = False  # Flag to prevent duplicate appending

		for comm in member_comm:# Check if the item has already been added for "عضوية وكيل لجنة"
			if not added_membership2:  
				if comm['salutation'] == 'عضوية لجنة خدمية':
					item_rate4 = frappe.get_all(
							"Item Price",
							filters={'price_list': self.price_list, 'item_code': 'عضوية لجنة خدمية'},
							fields=['item_code', 'item_name', 'price_list_rate'],
							limit=1
						)

					print(f"item rate 4 {item_rate4}")

					count4 = self.serv_count()

					if item_rate4:
						row4 = item_rate4[0]
						self.append("items", {
								'item_code': row4.get('item_code'),
								'item_name': row4.get('item_name'),
								'qty': count4,
								'rate': row4.get('price_list_rate'),
								'amount': count4 * row4.get("price_list_rate")
							})
						added_membership2 = True  # Set flag to True after appending the item



	@frappe.whitelist()
	def custom_prod_past_year(self,count):
		if self.select_service == 'تجديد العضوية' and self.year != datetime.now().year:
			exports = self.member_export_volume
			year = self.year
			
			service_data = frappe.get_doc("Service Generator", self.select_service)
			items = service_data.service_items

			group_name = None  # Initialize group_name outside the loop
			
			for row in exports:
				if row.year == year:
					customer_group = get_customer_group(row.total_amount_in_egp)
					group_name = customer_group[0].name  # Assign value to group_name

				if group_name:  # Ensure group_name is not None
					for row2 in items:
						if row2.category == group_name:
							self.append('items', {
								'item_code': row2.item,
								'item_name': row2.item,
								'qty': count
							})
			# time.sleep(3)
			# self.apply_price_list_rate()


	def get_last_serial_khetab(self):
		if self.select_service == 'إعادة طباعة خطاب المعمل المركزي':
			
			current_year = datetime.now().year
			from_date = f"{current_year}-01-01"
			to_date = f"{current_year}-12-31"
			invoice = frappe.get_all("Sales Invoice", 
									filters={'custom_service_group':'خطاب المعمل المركزي','status':'Paid','customer': self.member, 'posting_date': ['between',[from_date,to_date]],},
									fields=['name'],
									order_by='posting_date desc',
									limit=1)
			

			if len(invoice) > 0:
				items_last_print = frappe.get_all("Sales Invoice Item", filters={
				'parenttype': 'Sales Invoice',
				'parent': invoice[0]['name']
			},
			fields=['custom_khetab_print_serial'])
				print(items_last_print)
				self.last_central_lab_serial_printed = items_last_print[0]['custom_khetab_print_serial']

			else:
				frappe.throw(_("This Member Doesn't have Central laboratory letter this year"))





	def get_income_account(self):

		items = self.items

		for row in self.get('items'):
			all_data = frappe.get_all("Item Default", 
		filters={'parenttype':'Item','parent':row.item_code},
		fields=['income_account'])
			print(f"alldata {all_data}")
			if all_data:
				row.income_account = all_data[0]['income_account']




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
		central_print = request_doc.last_central_lab_serial_printed

		committees = frappe.get_all("Committees customer join", 
							  filters={'parent': doc_name},
							  fields=['committees','salutation'])
		
		vol = frappe.get_all("Volume of Exports In Years", 
					   filters={'parent': doc_name},
					   fields=['year','total_amount_in_egp','total_amount_in_usd','quantity_in_tons'])
		

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
			'year': year,
			'custom_service_group': service,
			'custom_invoice_type': 'Members',
			'custom_customer_outstanding_balance': member_outstanding,
			'custom_customer_group': member_category,
			'custom_volume_of_exports': volume_of_exports,
			'custom_customer_membership_status': membership_status,
			'custom_membership_status': payment_status,
			'custom_last_print_serial_for_reprint_khetab': central_print,
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
				'year': volumes['year'],
				'total_amount_in_egp': volumes['total_amount_in_egp'],
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
					'sales_invoice_ref': his['sales_invoice_ref'],
					'status': his['status']
				})
		
		if len(items) > 0:
			for item in items:
				new_invoice.append('items',{
					'item_code': item['item_code'],
					'item_name': item['item_name'],
					'qty': item['qty'],
					'rate': item['rate'],
					'amount': item['amount'],
					# 'custom_khetab_print_serial': central_print if central_print > 0 else print('mina is here')
				})

		new_invoice.append('payments',{
			'mode_of_payment': 'Cash',
			'amount': request_doc.total_amount
		})

		new_invoice.insert(ignore_permissions=True)


		return new_invoice.name
	
	except Exception as e:
		frappe.throw("Error in Creating Sales Invoice, Please Check all data in request")


@frappe.whitelist()
def get_service_print_format(serv):
	# service = self.select_service

	all_prints = frappe.get_all("Service Request Print Formats",
							  filters={'parenttype':"Service Generator", 'parent': serv},
							  fields=['print_format','print_button_name'])
	return all_prints


@frappe.whitelist()
def get_sales_invoice_print_format(serv):
	# service = self.select_service

	all_prints = frappe.get_all("Sales Invoice Print Formats",
							  filters={'parenttype':"Service Generator", 'parent': serv},
							  fields=['print_format','print_button_name'])
	return all_prints








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

# 	all_data = frappe.get_all("Volume Of Member Exports",
# 						   filters={'tax__number': tax_id},
# 						   fields=['year','total_amount_in_egp','total_amount_in_usd','quantity_in_tons'],
# 						   order_by='year desc')
# 	print(all_data)
# @frappe.whitelist()
# def get_member_exports(tax_id):
#     all_data = frappe.get_all(
#         "Volume Of Member Exports",
#         filters={'tax__number': tax_id},
#         fields=['year', 'total_amount_in_egp', 'total_amount_in_usd', 'quantity_in_tons'],
#         order_by='year desc'
#     )


#     unique_years = {}
#     for entry in all_data:
#         year = entry['year']
#         if year not in unique_years:
#             unique_years[year] = {
#                 'total_amount_in_egp': entry['total_amount_in_egp'],
#                 'total_amount_in_usd': entry['total_amount_in_usd'],
#                 'quantity_in_tons': float(entry['quantity_in_tons'])
#             }
    
    
#     total_amount_in_egp = sum(year_data['total_amount_in_egp'] for year_data in unique_years.values())
#     total_amount_in_usd = sum(year_data['total_amount_in_usd'] for year_data in unique_years.values())
#     quantity_in_tons = sum(year_data['quantity_in_tons'] for year_data in unique_years.values())

#     result = {
#         'total_amount_in_egp': total_amount_in_egp,
#         'total_amount_in_usd': total_amount_in_usd,
#         'quantity_in_tons': quantity_in_tons
#     }
    
#     print(result)
#     return result






frappe.whitelist()
def get_member_exportss(tax_id):
    all_data = frappe.get_all(
        "Volume Of Member Exports",
        filters={'tax__number': tax_id},
        fields=['year', 'total_amount_in_egp', 'total_amount_in_usd', 'quantity_in_tons'],
        order_by='year desc'
    )

    
    yearly_totals = {}
    for entry in all_data:
        year = entry['year']
        
        if year not in yearly_totals:
            yearly_totals[year] = {
                'total_amount_in_egp': 0,
                'total_amount_in_usd': 0,
                'quantity_in_tons': 0
            }
        
        # Add values for the year
        yearly_totals[year]['total_amount_in_egp'] += entry['total_amount_in_egp']
        yearly_totals[year]['total_amount_in_usd'] += entry['total_amount_in_usd']
        yearly_totals[year]['quantity_in_tons'] += float(entry['quantity_in_tons'])

    # Print totals for each year
    for year in sorted(yearly_totals.keys(), reverse=True):
        totals = yearly_totals[year]
        # print(f"Year: {year}")
        # print(f"  Total Amount in EGP: {totals['total_amount_in_egp']}")
        # print(f"  Total Amount in USD: {totals['total_amount_in_usd']}")
        # print(f"  Quantity in Tons: {totals['quantity_in_tons']}\n")
    
    return yearly_totals





