# # Copyright (c) 2024, ds and contributors
# # For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters):
    return [
        {
            "label": _("Member code"),
            "fieldname": "member",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150,
        },
        {
            "label": _("countries"),
            "fieldname": "country",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("التكتلات"),
            "fieldname": "clusters",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("CIO Name"),
            "fieldname": "custom_name_of_the_cioowner_of_the_company",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "label": _("Committee Name"),
            "fieldname": "committee_name",
            "fieldtype": "Link",
            "options": "Committee",
            "width": 200,
        },
        {
            "label": _("Total Amount in EGP"),
            "fieldname": "total_amount_in_egp",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": _("Total Amount in USD"),
            "fieldname": "total_amount_in_usd",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("current season"),
            "fieldname": "current_season",
            "fieldtype": "data",
            "width": 150,
        },
        {
            "label": _("Governorate code"),
            "fieldname": "territory_code",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Governorate"),
            "fieldname": "territory",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Membership status"),
            "fieldname": "custom_customer_status",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("CEO Mobile"),
            "fieldname": "customer_primary_contact",
            "fieldtype": "Data",
            "width": 200,
        },
        {"label": _("Email"), "fieldname": "email", "fieldtype": "Email", "width": 150},
    ]


def get_data(filters):
    conditions = []
    member = filters.get("member")
    country = filters.get("country")
    clusters = filters.get("clusters")
    custom_name_of_the_cioowner_of_the_company = filters.get(
        "custom_name_of_the_cioowner_of_the_company"
    )
    committee_name = filters.get("committee_name")
    territory = filters.get("territory")
    custom_customer_status = filters.get("custom_customer_status")
    if member:
        conditions.append("`tabCustomer`.`name` = %(member)s")
    else:
        conditions.append("`tabCustomer`.`name` IS NOT NULL")
    if country:
        conditions.append(
            "`tabVolume Of Member Exports`.`country_in_arabic` IN %(country_in_arabic)s"
        )
    if clusters:
        conditions.append("`tabCountries`.`geographical_clusters_name` IN %(clusters)s")
    if custom_name_of_the_cioowner_of_the_company:
        conditions.append(
            "`tabCustomer`.`custom_name_of_the_cioowner_of_the_company` = %(custom_name_of_the_cioowner_of_the_company)s"
        )
    if committee_name:
        conditions.append(
            "`tabCommittees you would like to join`.`committees` = %(committee_name)s"
        )
    if territory:
        conditions.append("`tabCustomer`.`territory` = %(territory)s")
    if custom_customer_status:
        conditions.append(
            "`tabCustomer`.`custom_customer_status` = %(custom_customer_status)s"
        )

    # Convert conditions list to a string for SQL query
    conditions_str = " AND ".join(conditions)
    if conditions_str:
        conditions_str = "WHERE " + conditions_str
    sql = f"""
        SELECT
            `tabCustomer`.`name` AS `member`,
            GROUP_CONCAT(DISTINCT `tabVolume Of Member Exports`.`country_in_arabic` SEPARATOR ', ') AS `country`,
            GROUP_CONCAT(DISTINCT `tabCountries`.`geographical_clusters_name` SEPARATOR ', ') AS `clusters`,
            `tabCustomer`.`custom_name_of_the_cioowner_of_the_company` AS `custom_name_of_the_cioowner_of_the_company`,
            GROUP_CONCAT(DISTINCT `tabCommittees you would like to join`.`committees` SEPARATOR ', ') AS `committee_name`,
            `tabVolume Of Member Exports for Three Years`.`total_amount_in_egp` AS `total_amount_in_egp`,
            CONCAT(FLOOR(`tabVolume Of Member Exports for Three Years`.`total_amount_in_usd`), ' $') AS `total_amount_in_usd`,
            CONCAT(YEAR(CURDATE()) - 2 , '-', YEAR(CURDATE()) - 1) AS `current_season`,
            `tabCustomer`.`territory` AS `territory_code`,
            `tabCustomer`.`governorate_name` AS `territory`,
            `tabCustomer`.`custom_ceo_mobile` AS `customer_primary_contact`,
            `tabCustomer`.`custom_customer_status` AS `custom_customer_status`,
            `tabCustomer`.`custom_email` AS `email`    
        FROM
            `tabVolume Of Member Exports`
        left JOIN `tabCustomer`
            ON `tabVolume Of Member Exports`.`tax__number` = `tabCustomer`.`tax_id`    
        LEFT JOIN `tabCommittees you would like to join`
            ON `tabCommittees you would like to join`.`parent` = `tabCustomer`.`name`
        LEFT JOIN `tabVolume Of Member Exports for Three Years`
            ON `tabVolume Of Member Exports for Three Years`.`parent` = `tabCustomer`.`name`

        Right JOIN `tabCountries`
            ON `tabCountries`.`name` = `tabVolume Of Member Exports`.`country_code`
        {conditions_str}
        GROUP BY `member`;
    """

    mydata = frappe.db.sql(
        sql,
        {
            "member": member,
            "country_in_arabic": country,
            "clusters": clusters,  # Pass clusters as a list
            "custom_name_of_the_cioowner_of_the_company": custom_name_of_the_cioowner_of_the_company,
            "committee_name": committee_name,
            "territory": territory,
            "custom_customer_status": custom_customer_status,
        },
        as_dict=True,
    )

    print(mydata)
    return mydata


# GROUP_CONCAT(DISTINCT `tabCountries`.`english_name` SEPARATOR ', ')AS country,
# 			GROUP_CONCAT(DISTINCT `tabCountries`.`geographical_clusters_name` SEPARATOR ', ') AS clusters,


#     inner JOIN `tabCountries`
# 			ON `tabCountries`.`name` = `tabVolume Of Member Exports`.`country_code`