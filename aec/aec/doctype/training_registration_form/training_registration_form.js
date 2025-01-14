// Copyright (c) 2025, ds and contributors
// For license information, please see license.txt



frappe.ui.form.on('Training Registration Form', {
    send_mail: function(frm) {
        
        const sender_mail = frm.doc.email_sender;
        const subject = frm.doc.subject;
        const body_mail = frm.doc.body_mail;
        const email_reciver = frm.doc.email;

        if (!sender_mail || !subject || !body_mail || !email_reciver) {
            frappe.msgprint(__("Please fill all the required fields (Sender Mail, Subject, Body Mail, and Email Receiver)."));
            return;
        }

        frappe.call({
            method: 'aec.aec.doctype.training_registration_form.training_registration_form.send_email',
            args: {
                sender_mail: sender_mail,
                subject: subject,
                body_mail: body_mail,
                email_reciver: email_reciver
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
