# Copyright (c) 2024, ds and contributors
# For license information, please see license.txt
import ast
import frappe
from frappe.model.document import Document

class Exhibitions(Document):
	pass
class Exhibitions(Document):
    pass

@frappe.whitelist()
def get_contact_exhibition(committee, status,name,docname):
    # Validate input parameters
    if not status:
        frappe.throw("Select status")
    if not committee:
        frappe.throw("Select Committee")
    condition = []
    if isinstance(status, str):
        list_value = ast.literal_eval(status)
        status_tuple = tuple(list_value)

    # # Build the condition string
    condition_str1 = f" WHERE emails.email_id IS NOT NULL AND tcj.`committees` = '{committee}' AND tc.`custom_customer_status` IN {status_tuple}"
    condition_str2 = f" WHERE tc.custom_email IS NOT NULL AND tcj.`committees` = '{committee}' AND tc.`custom_customer_status` IN {status_tuple}"
    # SQL query
    sql = f"""
        SELECT 
    tc.name AS customer_name,
    emails.link_name,
    emails.email_id AS email, -- First email source
    tc.custom_email
FROM `tabCustomer` tc
left JOIN `tabCommittees you would like to join` tcj

ON tc.`name` = tcj.`parent`
LEFT JOIN (
    SELECT 
        dl.link_name, 
        c.custom_contact_type,
        ce.email_id
    FROM `tabContact` c
    LEFT JOIN `tabContact Email` ce
       ON ce.parent = c.name
    LEFT JOIN `tabDynamic Link` dl 
        ON c.name = dl.parent      
    WHERE c.custom_contact_type = 'Exhibition'
) AS emails
ON tc.name = emails.link_name 
{condition_str1}
UNION ALL

SELECT 
    tc.name AS customer_name,
    emails.link_name,
    tc.custom_email AS email, -- Second email source
    tc.custom_email
FROM `tabCustomer` tc
left JOIN `tabCommittees you would like to join` tcj

ON tc.`name` = tcj.`parent`

LEFT JOIN (
    SELECT 
        dl.link_name, 
        c.custom_contact_type,
        ce.email_id
    FROM `tabContact` c
    LEFT JOIN `tabContact Email` ce
       ON ce.parent = c.name
    LEFT JOIN `tabDynamic Link` dl 
        ON c.name = dl.parent      
    WHERE c.custom_contact_type = 'Exhibition'
) AS emails
ON tc.name = emails.link_name 

{condition_str2}
ORDER BY customer_name;

        
    """
    data = frappe.db.sql(sql, as_dict=True)
    letter = frappe.new_doc("Customer Newsletter")
    letter.source = docname
    letter.generalization_id = name
    for row in data:
      letter.append("customer_email",{
          "email":row['email']
      })
    letter.save()  
    frappe.db.commit()
    return letter
