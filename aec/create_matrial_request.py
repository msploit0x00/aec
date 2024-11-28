import frappe
from frappe import _


@frappe.whitelist()
def create_matrial_request(material_request_type, transaction_date, items,source,source_name):
    # Ensure items are passed correctly and in the expected format (list of dicts)
    if items:
        # return {"error": "Items should be a list of dictionaries",}
        items = frappe.parse_json(items)  # Parse the JSON string into a Python list
        # Log the items to see the structure
        frappe.logger().info(f"Items: {items}")

        # Create the Material Request Document
        mr = frappe.get_doc(
            {
                "doctype": "Material Request",
                "material_request_type": material_request_type,
                "transaction_date": transaction_date,
                "items": items,
                "custom_source": source,
                "custom_source_record": source_name
            }
        )

        # Insert the document into the database
        mr.insert()
        mr.save()

        # Commit changes to the database
        # frappe.db.commit()

        # Return success message
        return {
            "message": _("Material Request created successfully"),
            "mr_name": mr.name,
        }


#  [
# 					{
# 						"item_code": "_Test Item",
# 						"qty": 1,
# 						"uom": "_Test UOM",
# 						"warehouse": "_Test Warehouse - _TC",
# 						"schedule_date": nowdate(),
# 						"rate": 100000,
# 						"expense_account": "_Test Account Cost for Goods Sold - _TC",
# 						"cost_center": "_Test Cost Center - _TC",
# 					}
# 				],