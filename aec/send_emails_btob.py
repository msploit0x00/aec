import frappe
from frappe import _


@frappe.whitelist()
def send_email(name, body, docname):
    print("Sending email...")

    # Fetch the document based on 'name'
    doc = frappe.get_doc(docname, name)

    recipients = [member.email for member in doc.targeted_companies]
    
    args = doc.as_dict()

    args["message"] = get_message(doc, body)

    email_args = {
        "subject": doc.subject,
        "sender": doc.sender_mail_for_buyers,
        "recipients": recipients,
        "attachments": get_attachments(doc),
        "template": "newsletter",
        "reference_doctype": doc.doctype,
        "reference_name": doc.name,
        "queue_separately": True,
        "send_priority": 0,
        "args": args,
    }
    frappe.sendmail(**email_args)
    print("AAAAAAAAAAAA",email_args)
    frappe.msgprint(
        _("Email have sent successfully")
    )


def get_message(doc, body):
    date_member = [{"date": member.date, "email": member.email} for member in doc.targeted_companies]  
    messages = []
    for recipient in date_member:
      content = body
      if doc.meeting_link:
        content += f"<p>{doc.meeting_link}</p>"
      if doc.meeting_location:
        content += f"<p>{doc.meeting_location}</p>"
      content += f"<p>Date is : {recipient['date']}</p>"
      render_template = frappe.render_template(content, {"doc": doc.as_dict()})
      messages.append(render_template)
      print("render_template is ======= ",render_template)
    return messages
    

  
def get_attachments(doc):
    return [{"file_url": row.attachment} for row in doc.attachments]
