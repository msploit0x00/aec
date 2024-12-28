# Copyright (c) 2024, ds and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
class ExhibitionsAnnualPlan(Document):
  pass
@frappe.whitelist()
def make_exhibitions(row):
  child = json.loads(row)
  exhibition = frappe.new_doc("Exhibitions")
  exhibition.name1 = child.get("arabic_name")
  exhibition.english_name = child.get("english_name") 
  exhibition.exhibition_specialty = child.get("exhibition_specialty")
  exhibition.registration_date = child.get("date_from")
  exhibition.valid_to = child.get("date_to")
  exhibition.exhibition_type = child.get("exhibition_type")
  exhibition.append("countries", {
    "country":child.get("country")
  })
  exhibition.save()
  frappe.db.commit()
  return exhibition

@frappe.whitelist()
def create_tranning_annual_reminder(row):
  return row