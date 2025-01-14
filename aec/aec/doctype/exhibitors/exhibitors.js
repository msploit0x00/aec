

// frappe.ui.form.on('Exhibitors', {
// 	// refresh: function(frm) {

// 	// }
// });


frappe.ui.form.on('Exhibitors', {
    send_email: function(frm) {
        const sender_mail = frm.doc.sender_email;

		// var sender = frappe.model.get_value("Email Account", sender_mail,'email_id');

		var sender = frm.doc.email;


        const subject = frm.doc.subject;
        const body_mail = frm.doc.body_mail;
        const list_reciver = frm.doc.email_ids.map(function(row){
			return row.email_id;
		});
		console.log(list_reciver);

        if (!sender_mail || !subject || !body_mail || list_reciver.length === 0) {
            frappe.msgprint(__("Please fill all the required fields (Sender Mail, Subject, Body Mail, Table of emails is empty )."));
            return;
        }

        frappe.call({
            method: 'aec.aec.doctype.exhibitors.exhibitors.send_email_list',
            args: {
                sender_mail: sender,
                subject: subject,
                body_mail: body_mail,
				list_reciver: list_reciver,
            },
            callback: function(r) {
                if (r.message) {
                    frappe.msgprint(__("Email sent successfully!"));
                } else {
                    frappe.msgprint(__("Failed to send email. Please try again."));
                }
            }
        });
    }
});
