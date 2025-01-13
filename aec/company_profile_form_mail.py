import frappe





@frappe.whitelist(allow_guest=True)
def send_mail_for_company_profile(email):

    frappe.sendmail()

    
    
    