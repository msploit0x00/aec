import frappe
from frappe import _


@frappe.whitelist()
def send_email(name, body):
    print("Sending email...")

    # Fetch the document based on 'name'
    doc = frappe.get_doc("Business to Business Meetings", name)

    recipients = [member.email for member in doc.members_info]
    args = doc.as_dict()
    args["message"] = get_message(doc, body)

    email_args = {
        "subject": doc.members_subject,
        "sender": doc.sender_mail_for_members,
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
        _(
            "Your ..................................................Email sent successfully"
        )
    )


def get_message(doc, body):
    content = frappe.render_template(
        body + doc.meeting_link + doc.meeting_location, {"doc": doc.as_dict()}
    )
    return content


def get_attachments(doc):
    return [{"file_url": row.attachment} for row in doc.attachment]