# Copyright (c) 2024, ds and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.accounts.utils import get_balance_on

class ServiceRequest(Document):
	def validate(self):
		self.validate_customer()
		self.get_member_committees()
		self.allow_outstanding()
		self.show_export_volumes()



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

		if(service_data.allow_outstanding == 1 and outstanding > 0.0):
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
		
		
		
			