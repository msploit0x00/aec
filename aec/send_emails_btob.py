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
    frappe.msgprint(
        _("Your Email sent successfully")
    )


def get_message(doc, body):
    # Create a list of dictionaries containing date and member
    date_member = [{"date": member.date, "member": member.member} for member in doc.targeted_companies]
    
    content = body  # Start with the body content

    # Safely concatenate meeting_link and meeting_location if they are not None
    if doc.meeting_link:
        content += f"<p>{doc.meeting_link}</p>"
    if doc.meeting_location:
        content += f"<p>{doc.meeting_location}</p>"

    # Append the date and member values
    for d in date_member:
        # Ensure you're accessing the dictionary keys correctly
        content += f"<p>Date: {d['date']}, Member: {d['member']}</p>"

    # Render the template with the updated content
    content = frappe.render_template(content, {"doc": doc.as_dict()})

    return content


def get_attachments(doc):
    return [{"file_url": row.attachment} for row in doc.attachments]
