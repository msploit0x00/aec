// Copyright (c) 2024, ds and contributors
// For license information, please see license.txt

frappe.ui.form.on('Service Request', {
	member(frm){
		// if(frm.doc.memebr){
			
		// 	frm.set_value("member_outstanding")

		// }

		frappe.call({
			method: "erpnext.accounts.utils.get_balance_on",
			args: {party_type: 'Customer', party: frm.doc.customer},
			callback: function(r) {
			frm.doc.member_outstanding = r.message;
			// refresh_field('member_outstanding');
			console.log("Done");
			}
			});














	},


	items_add(frm,cdt, cdn) {
		var row = frappe.get_doc(cdt, cdn);
		this.frm.script_manager.copy_from_first_row("items", row, ["income_account", "discount_account", "cost_center"]);
	},

    // income_account: function(frm) {
    //     erpnext.utils.copy_value_in_all_rows(frm.doc, null, null, "items", "income_account");
    // },
    
    // expense_account: function(frm) {
    //     erpnext.utils.copy_value_in_all_rows(frm.doc, null, null, "items", "expense_account");
    // },
    
    // cost_center: function(frm) {
    //     erpnext.utils.copy_value_in_all_rows(frm.doc, null, null, "items", "cost_center");
    // }


	select_service(frm) {
		if (frm.doc.select_service) {
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Service Generator",
					name: frm.doc.select_service
				},
				callback: function(r) {
					let filter_conditions = [];
					let service_data = r.message;
	
				
					if (service_data.active == 1 || service_data.inactive == 1 || 
						service_data.request == 1 || service_data.suspended == 1 || 
						service_data.data_completion == 1) {
						
						
						let statuses = [];
						if (service_data.active == 1) statuses.push("Active");
						if (service_data.inactive == 1) statuses.push("Inactive");
						if (service_data.request == 1) statuses.push("Requested");
						if (service_data.suspended == 1) statuses.push("Suspended");
						if (service_data.data_completion == 1) statuses.push("Data Completion");
	
					
						filter_conditions.push(["custom_customer_status", "in", statuses]);
					}
	
					// Apply the filters to the 'member' field
					frm.set_query('member', function() {
						return {
							filters: filter_conditions
						};
					});
	
					frm.refresh_field('member');
				}
			});
		}
	}
	



});
