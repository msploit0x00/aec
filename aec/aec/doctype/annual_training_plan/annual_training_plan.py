# Copyright (c) 2024, ds and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AnnualTrainingplan(Document):
  def on_submit(self):
      table = self.training_plan
      if not table:
         frappe.throw("please full table Plan Training")
      else:   
        for row in table:
            reminder = frappe.new_doc("Training Annual Reminder")
            reminder.topic = row.topic
            reminder.month = row.month
            reminder.training_date =row.date
            reminder.training_days = row.training_days
            reminder.number_of_instructor = row.number_of_instructor
            reminder.expected_trainees = row.expected_trainees
            reminder.hospitality_costs = row.hospitality_costs
        reminder.save()
        frappe.db.commit()
