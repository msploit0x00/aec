# Copyright (c) 2025, ds and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TrainingRegistrationForm(Document):
	pass



@frappe.whitelist()
def send_email(sender_mail, subject, body_mail, email_reciver):
    try:
        # Send email using frappe.sendmail
        frappe.sendmail(
            sender= sender_mail,
            recipients= email_reciver,
            subject= subject,
            message= body_mail
        )
        return "Email sent successfully!"
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Failed to send email")
        return f"Failed to send email: {str(e)}"
