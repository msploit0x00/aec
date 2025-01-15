# Copyright (c) 2025, ds and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ExhibitionFollowUp(Document):
	pass



# Get Emails

@frappe.whitelist()
def get_emails_from_exhibitors(exhibition, status):
	
	emails = []
	
	
	exhibitors_name = frappe.get_list("Exhibitors",
									 filters={
										 'exhibitions': exhibition,
										 'status': status, 
									 },
									 fields=['name'])
	
	# print(exhibitors_name)


	for row in exhibitors_name:
		all_email = frappe.get_all("Contact Email", filters={'parent': row.name }, fields=['email_id'])
		# print(all_email)

		#  Flatten the nested list
		flattened_emails = [email for sublist in emails for email in sublist]

		#  Extract email IDs
		email_list = [email['email_id'] for email in flattened_emails]

		#  Remove duplicates (optional)
		unique_email_list = list(set(email_list))

		
		# print("All Emails:", email_list)
		# print("Unique Emails:", unique_email_list)


		emails.append(all_email)


	return unique_email_list


#----------------------------------------------------------------------------------------------------

# Send Emails



@frappe.whitelist()
def send_email_list(name,sender_mail, subject, attachment,body_mail, list_reciver):
    
    if(attachment):
         doc = frappe.get_doc("Exhibition Follow Up", name)
       
    try:

        # If list_reciver is a string, clean it and split into a list
        if isinstance(list_reciver, str):
            # Remove unwanted characters like [, ], ", and '
            list_reciver = list_reciver.replace("[", "").replace("]", "").replace('"', '').replace("'", "")
            # Split into a list of emails
            list_reciver = list_reciver.split(',')
        
		
            
        # Loop through each recipient and send an email
        for reciver in list_reciver:
            # Strip any leading/trailing whitespace from the email address
            reciver = reciver.strip()
            
            # Ensure the email is not empty
            if reciver:
                frappe.sendmail(
                    sender=sender_mail,
                    recipients=reciver,
                    attachments=get_attachments(doc),
                    subject=subject,
                    message=body_mail
                )
        
        return "Emails sent successfully!"
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Failed to send email")
        return f"Failed to send email: {str(e)}"


def get_attachments(doc):
    return [{"file_url": row.attachment} for row in doc.attachments]