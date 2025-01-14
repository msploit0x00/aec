# Copyright (c) 2024, ds and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Exhibitors(Document):
	pass


@frappe.whitelist()
def send_email_list(sender_mail, subject, body_mail,list_reciver):
    try:
        # frappe.msgprint('list of reciver is: '+ list_reciver)
        frappe.sendmail(
            sender= sender_mail,
            recipients= list_reciver,
            subject= subject,
            message= body_mail
        )
        return "Email sent successfully!"
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Failed to send email")
        return f"Failed to send email: {str(e)}"
