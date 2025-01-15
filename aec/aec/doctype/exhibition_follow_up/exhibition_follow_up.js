// Copyright (c) 2025, ds and contributors
// For license information, please see license.txt




frappe.ui.form.on('Exhibition Follow Up', {
// if doc is submited
    refresh: function(frm){
        if(frm.doc.docstatus === 1 ){
            frm.add_custom_button(__("Send Mail"), function () {
                frm.events.Send(frm);
              });
        }
        
    },





// Get Emails

    get_emails: function(frm) {
        frappe.call({
            method: 'aec.aec.doctype.exhibition_follow_up.exhibition_follow_up.get_emails_from_exhibitors',
            args: {
                'exhibition': frm.doc.exhibitions,
                'status': frm.doc.status
            },
            callback: function(r) {
                if (r.message) {
					console.log(r.message);
                    // Clear existing emails in the child table
                    frm.clear_table('exhibitors_emails');
                    
                    // Add new emails to the child table
                    r.message.forEach(function(email) {
                        var child = frm.add_child('exhibitors_emails');
                        child.email = email;
                    });
                    
                    // Refresh the form to show the updated child table
                    frm.refresh_field('exhibitors_emails');
                }
            }
        });
    },

    
    
    //------------------------------------------------------------------------
    // Send Emails
    Send: function (frm) {
        const name = frm.doc.name;
		const sender_mail = frm.doc.custom_email_sender;
        const subject = frm.doc.subject;
        const attachment = frm.doc.attachments;
        const body_mail = frm.doc.body_mail;
        let list_reciver = [];
        frm.doc.exhibitors_emails.forEach((row)=>{
            list_reciver.push(row.email);
        });
        
        

        console.log(list_reciver);
        console.log(attachment);
        
		
        
        if (!sender_mail || !subject || !body_mail || list_reciver.length === 0) {
            frappe.msgprint(__("Please fill all the required fields (Sender Mail, Subject, Body Mail, Table of emails is empty )."));
            return;
        }

        frappe.call({
            method: 'aec.aec.doctype.exhibition_follow_up.exhibition_follow_up.send_email_list',
            args: {
                name: name,
                sender_mail: sender_mail,
                subject: subject,
                attachment : attachment,
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
      },

});



