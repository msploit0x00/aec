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
	},


	
	before_save(frm){


		if(frm.doc.select_service){
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Service Generator",
					name: frm.doc.select_service,
				},
				callback(r) {
					if(r.message) {
						if(r.message.show_export_volume == 1){
							frm.set_df_property('member_export_volume', 'hidden', 0);
							console.log("Hidden Off");
						}else{
							console.log("Hidden On");
						}


						if(r.message.show_committees == 1){
							frm.set_df_property('committees_member_join', 'hidden', 0);
							console.log("Hidden Off 2");

						}else{
							console.log("Hidden On 2");
						}




					}
				}
			});




		}




	},


	refresh(frm) {
		if (frm.doc.select_service) {
			frm.call({
				method: "get_service_print_format",
				args: {
					'serv': frm.doc.select_service,
				},
				callback: function(response) {
					if (response.message) {
						var prints = response.message;
	
			
						frm.clear_custom_buttons();
	
						for (let row of prints) {
				
							frm.add_custom_button(__(row.print_button_name), function() {
			
								frappe.utils.print(
									frm.doctype,            
									frm.docname,            
									row.print_format,
									"العربية",      
									// frm.doc.letter_head
								);
								__("Create")
							});
	
							// Set the button group as primary
							// frm.page.set_inner_btn_group_as_primary(__('Create'));
						}
					}
				}
			});
		}



		/////show comittess ot not
		frappe.db.get_value('Service Generator', cur_frm.doc.select_service,'show_committees')
		.then(value => {
			console.log(value.message.show_committees);
			

			if(value.message.show_committees == 1){

				frm.set_df_property('committees_member_join', 'hidden', 0);




			}else{
				frm.set_df_property('committees_member_join', 'hidden', 1);

			}
			
			console.log("committtttttttt");
			
			
		});



		/////show export volumes or not based on settings
		frappe.db.get_value('Service Generator', cur_frm.doc.select_service,'show_export_volume')
		.then(value => {
			console.log(value.message.show_committees);
			

			if(value.message.show_export_volume == 1){

				frm.set_df_property('member_export_volume', 'hidden', 0);




			}else{
				frm.set_df_property('member_export_volume', 'hidden', 1);

			}
			
			console.log("committtttttttt");
			
			
		});










	},


	member(frm){
		frappe.call({
			method: "erpnext.accounts.utils.get_balance_on",
			args: {date: frm.doc.posting_date, party_type: 'Customer', party: frm.doc.member},
			callback: function(r) {
			frm.doc.member_outstanding = r.message;
			refresh_field('member_outstanding');
			}
			});
	},




	// get_outstanding_invoices(frm){
	// 	// // frm.events.get_member_history(frm);
		
	// 	// frm.call('get_member_history');

	// 	// // if(frm.doc.select_service == 'تجديد العضوية'){
	// 	// // 	frm.call('get_member_history');

	// 	// // }else{

	// 	// // frm.call('get_member_outstanding_invoices');
	// 	// // }
	// 	// frm.save();

	// 	let d = new frappe.ui.Dialog({
	// 		title: 'Member Outstanding Invoices',
	// 		fields: [
	// 			{
	// 				fieldname: "outstanding_sales_invoices",
	// 				fieldtype: "Table",
	// 				label: __("Sales Invoices"),
	// 				in_place_edit: true,
	// 				reqd: 1,
	// 				fields: [
	// 					{
	// 						fieldname: "sales_invoice",
	// 						label: __("Sales Invoice"),
	// 						fieldtype: "Link",
	// 						options:"Sales Invoice",
	// 						in_list_view: 1,
	// 						// reqd: 1,
	// 					}
	// 				],
	// 		size: 'large',
	// 		primary_action_label: 'Submit',
	// 		primary_action(values) {
	// 			if (!values.first_name || !values.last_name) {
	// 				frappe.msgprint('Please enter both first and last names.');
	// 				return;
	// 			}
		
	// 			// Fetch outstanding invoices
	// 			frappe.call({
	// 				method: "aec.aec.doctype.service_request.service_request.get_member_outstanding_invoices",
	// 				args: {
						
	// 				},
	// 				callback: function(r) {
	// 					if (r.message && r.message.length > 0) {
	// 						let invoices = r.message;
	// 						let html_content = invoices.map(invoice => 
	// 							`<tr>
	// 								<td>${invoice.name}</td>
	// 								<td>${invoice.posting_date}</td>
	// 								<td>${invoice.outstanding_amount}</td>
	// 							</tr>`
	// 						).join("");
		
	// 						let invoice_dialog = new frappe.ui.Dialog({
	// 							title: `Outstanding Invoices for ${values.first_name} ${values.last_name}`,
	// 							fields: [
	// 								{
	// 									fieldtype: "HTML",
	// 									options: `
	// 										<table class="table table-bordered">
	// 											<thead>
	// 												<tr>
	// 													<th>Invoice</th>
	// 													<th>Date</th>
	// 													<th>Outstanding Amount</th>
	// 												</tr>
	// 											</thead>
	// 											<tbody>
	// 												${html_content}
	// 											</tbody>
	// 										</table>
	// 									`
	// 								}
	// 							],
	// 							primary_action_label: "Close",
	// 							primary_action: function() {
	// 								invoice_dialog.hide();
	// 							}
	// 						});
	// 						invoice_dialog.show();
	// 					} else {
	// 						frappe.msgprint('No outstanding invoices found.');
	// 					}
	// 				}
	// 			});
		
	// 			d.hide();
	// 		}
	// 	});
		
	// 	d.show();
		






















	// },


	// get_member_history: function (frm) {
	// 	// frm.save();
	// 	frappe.call({
	// 	  method: "get_member_history",
	// 	  doc: frm.doc,
	// 	  args: {
	// 		// show_progress: 1,
	// 	  },
	// 	  freeze: true,
	// 	  callback: function () {
	// 		// frappe.hide_progress();
	
	// 		// frm.refresh();
	// 	  },
	// 	});
	//   },


	



});



frappe.ui.form.on('Service Request Item', {
	qty(frm,cdt,cdn) {
		
		var row = locals[cdt][cdn];

		// if(qty){

			var rate = row.rate;
			var amount = row.qty * rate;

			frappe.model.set_value(cdt,cdn,'amount', amount);


		// }



	}
})











// function print(print_format,label){




// }

		
// if(doc.custom_supply_order_type === "Partial Supply Order" && doc.docstatus == 1){
// 	//  cur_frm.page.set_inner_btn_group_as_primary(__('Create'));
// 			  this.frm.add_custom_button(
// 				  __("Create Sales Order"),
// 				  () => this.make_sales_order(),
// 				  __("Create")
// 			  );
	  
// 	  cur_frm.page.set_inner_btn_group_as_primary(__('Create'));
	  
//   }