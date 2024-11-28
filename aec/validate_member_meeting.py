import frappe


@frappe.whitelist()
def get_meeting(member, date, time_from, time_to):
    # Initialize conditions list
    conditions = []

    # Add conditions if provided
    if member:
        conditions.append("mi.member = %(member)s")
    if date:
        conditions.append("mi.date = %(date)s")
    if time_from:
        # Adding the condition to filter time range using BETWEEN
        conditions.append("%(time_from)s BETWEEN mi.time_from AND mi.time_to")
    # Join conditions with AND
    conditions_str = " AND ".join(conditions)
    if conditions_str:
        conditions_str = "WHERE " + conditions_str

    # SQL Query to fetch meeting data
    sql = """
        SELECT 
            btb.name,
            mi.member,
            mi.date,
            mi.time_from,
            mi.time_to  
        FROM 
            `tabBusiness to Business Meetings` AS btb
        LEFT JOIN 
            `tabMembers Info` AS mi ON mi.parent = btb.name
        {conditions_str}
    """.format(
        conditions_str=conditions_str
    )

    # Execute query with provided parameters
    meetings = frappe.db.sql(
        sql, {"member": member, "date": date, "time_from": time_from}, as_dict=True
    )

    if meetings:
        frappe.msgprint(
            f"meeting for {time_from} for Member {member} is already exists"
        )
    if not meetings:
        if member:
            conditions.append("mi.member = %(member)s")
        if date:
            conditions.append("mi.date = %(date)s")
        if time_to:
            # Adding the condition to filter time range using BETWEEN
            conditions.append("%(time_to)s BETWEEN mi.time_from AND mi.time_to")
            conditions_str = " AND ".join(conditions)
            if conditions_str:
                conditions_str = "WHERE " + conditions_str
            sql = """
                SELECT 
                    btb.name,
                    mi.member,
                    mi.date,
                    mi.time_from,
                    mi.time_to  
                FROM 
                    `tabBusiness to Business Meetings` AS btb
                LEFT JOIN 
                    `tabMembers Info` AS mi ON mi.parent = btb.name
                {conditions_str}
            """.format(
                conditions_str=conditions_str
            )
            meetings_to_time = frappe.db.sql(
                sql,
                {
                    "member": member,
                    "date": date,
                    "time_from": time_from,
                    "time_to": time_to,
                },
                as_dict=True,
            )
            if meetings_to_time:
                frappe.msgprint(
                    f"meeting  {time_to} for Member{member} is already exists"
                )