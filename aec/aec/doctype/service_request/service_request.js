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














	}
});
