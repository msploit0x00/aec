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
	}

    // income_account: function(frm) {
    //     erpnext.utils.copy_value_in_all_rows(frm.doc, null, null, "items", "income_account");
    // },
    
    // expense_account: function(frm) {
    //     erpnext.utils.copy_value_in_all_rows(frm.doc, null, null, "items", "expense_account");
    // },
    
    // cost_center: function(frm) {
    //     erpnext.utils.copy_value_in_all_rows(frm.doc, null, null, "items", "cost_center");
    // }



});
