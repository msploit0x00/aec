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



	validate:function(frm){



		var items = frm.doc.items

		for(let row of items){
			if (row.matched == 0){
				frappe.msgprint(__("This Row doesn't have a match sales invoice in row " + row.idx));

				frappe.validated = false

			}
		}





		frm.call("get_mosanda_serial").then(response => {
			// Handle the response
			if (response.message) {
				// console.log("Mosanda Serial: ", response.message);
				// You can update a field in the form with the response
				// frm.set_value("mosanda_serial", response.message);

				frappe.msgprint(response.message);
			} else {
				frappe.msgprint("No serial received.");
			}
		})


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
									"No Letterhead",
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
			
			// console.log("committtttttttt");
			
			
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
			
			// console.log("committtttttttt");
			
			
		});


		frappe.db.get_value('Service Generator', cur_frm.doc.select_service,'depend_on')
		.then(value => {
			console.log(value.message.show_committees);
			

			if(value.message.depend_on == 1){

				frm.set_df_property('last_record', 'hidden', 0);




			}else{
				frm.set_df_property('last_record', 'hidden', 1);

			}
			
			// console.log("committtttttttt");
			
			
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

	// 	let d = new frappe.ui.form.MultiSelectDialog({
	// 		doctype: "Sales Invoice", // Target doctype for outstanding invoices
	// 		target: this.cur_frm,     // Current form as the target
	// 		setters: {                // Pre-fill fields in the dialog
	// 			customer: null,
	// 			posting_date: null
	// 		},
	// 		add_filters_group: 1,     // Allows users to add custom filters in the dialog
	// 		date_field: "posting_date", // Adds a date range filter for this field
	// 		get_query() {             // Client-side query method
	// 			return {
	// 				filters: {
	// 					docstatus: 1,          // Only submitted invoices
	// 					outstanding_amount: [">", 0] // Only invoices with outstanding amounts
	// 				}
	// 			};
	// 		},
	// 		action(selections) {      // Action to perform on selections
	// 			console.log(selections); // Outputs selected records to the console
	// 			// You can add further processing logic here based on selections
	// 		}
	// 	});
		
		
	// 	d.show();


	// },


	// get_outstanding_invoices(frm) {
	// 	let d = new frappe.ui.form.MultiSelectDialog({
	// 		doctype: "Sales Invoice", // Target doctype for outstanding invoices
	// 		target: frm,              // Current form as the target
	// 		setters: {                // Pre-fill fields in the dialog
	// 			customer: cur_frm.doc.member,
	// 			posting_date: null
	// 		},
	// 		add_filters_group: 1,     // Allows users to add custom filters in the dialog
	// 		date_field: "posting_date", // Adds a date range filter for this field
	// 		coulmns: ['name','status','custom_service_group','outstanding_amount','year'],
	// 		get_query() {             // Client-side query method
	// 			return {
	// 				filters: {
	// 					status: ['in',['Unpaid','Overdue','Partly Paid']],          // Only submitted invoices
	// 					outstanding_amount: [">", 0] // Only invoices with outstanding amounts
	// 				}
	// 			};
	// 		},
	// 		action(selections) {      // Action to perform on selections
	// 			console.log(selections); // Outputs selected records to the console
	// 			// Additional processing can go here, such as saving or updating values
	// 		}
	// 	});
		
	// 	d.show(); // Show the dialog
	// }
	
	get_outstanding_invoices(frm) {
		let d = new frappe.ui.form.MultiSelectDialog({
			doctype: "Sales Invoice", 
			target: frm,              
			setters: {                
				customer: cur_frm.doc.member,
				posting_date: null,
				status: 'Overdue',
				custom_service_group:null,
				outstanding_amount:null
			},
			primary_action_label: " ",
			secondary_action_label:".",
			secondary_action:"",
			// add_filters_group: 1,     
			date_field: "posting_date",
			fields: ['name', 'status', 'custom_service_group', 'outstanding_amount', 'year', 'customer_name', 'invoice_type'], // Added extra columns
			get_query() {             
				return {
					filters: {
						status: ['in', ['Unpaid', 'Overdue', 'Partly Paid']],
						docstatus: 1,          // Only submitted invoices
						outstanding_amount: [">", 0.00] // Only invoices with outstanding amounts
					}
				};
			},
			// hide_actions: true,
			// primary_action_label: [],
			// secondary_action_label: [],
			action(selections) {      // Action to perform on selections
				console.log(selections); // Outputs selected records to the console
				// Additional processing can go here, such as saving or updating values
			},
			size: 'large'
		});
		// d.primary_action_label.hide();
		// d.show(); // Show the dialog
		// $(d.wrapper).find('.modal-footer').remove();
		// $(d.wrapper).find('.modal-footer .btn-secondary').hide(); // Hides the Cancel button
// $(d.wrapper).find('.modal-footer .btn-primary').hide();   // Hides the Select button


	}
	



















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


// frappe.ui.form.on('Service Request Item', {
// 	to_serial(frm,cdt,cdn) {
		
// 		var row = locals[cdt][cdn];

// 		// if(qty){

// 		frm.call("get_mosanda_serial")


// 		// }



// 	}
// })







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