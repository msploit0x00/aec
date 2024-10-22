// Copyright (c) 2024, ds and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Export Opportunites Generalization2"] = {
	filters: [
	  {
		fieldname: "member",
		label: __("Customer"),
		fieldtype: "Link",
		options: "Customer",
		width: "200px",
	  },
  
	  {
		fieldname: "committee_name",
		label: __("Please insert Committee"),
		fieldtype: "Link",
		options: "Committee",
		width: "350px",
	  },
	  {
		fieldname: "territory_code",
		label: __("Please Select Governorate"),
		fieldtype: "Link",
		options: "Territory",
		width: "350px",
	  },
  
	  {
		fieldname: "custom_customer_status",
		label: "Please select Membership Status",
		fieldtype: "Select",
		options: [
		  "",
		  "Requested",
		  "Requested From Website",
		  "Active",
		  "Inactive",
		  "Suspended",
		  "استيفاء بيانات",
		],
		default: "",
	  },
	  {
		fieldname: "name_of_the_cioowner_of_the_company",
		label: __("Please write CIO arabic"),
		fieldtype: "Data",
		width: "200px",
	  },
	  {
		fieldname: "select",
		label: __("put number of row"),
		fieldtype: "Int",
		width: "200px",
		on_change: function (report) {
		  var values = report.get_values();
		  var intValue = values.select;
		  $(".dt-row").find(":input[type=checkbox]").prop("checked", false);
  
		  if (!isNaN(intValue) && intValue > 0) {
			// Start selecting from row 2 (index 1)
			$(".dt-row").each(function (index) {
			  if (index >= 2 && index < 2 + intValue) {
				// Select 10 rows starting from row 2
				$(this).find(":input[type=checkbox]").prop("checked", true);
			  }
			});
		  }
		  console.log("value", intValue);
		},
	  },
	  // You can add more filters here as per your requirement
	],
	get_datatable_options(options) {
	  return Object.assign(options, {
		checkboxColumn: true,
	  });
	},
	onload: function (report) {
	  report.page.add_inner_button(__("Get Selected"), function () {
		var values = report.get_values();
		var member = values.member;
		var committee_name = values.committee_name;
		var territory = values.territory;
		var custom_customer_status = values.custom_customer_status;
		var name_of_the_cioowner_of_the_company =
		  values.name_of_the_cioowner_of_the_company;
		var selected_rows = [];
		$(".dt-scrollable")
		  .find(":input[type=checkbox]")
		  .each((idx, checkbox) => {
			if (checkbox.checked) {
			  var rowData = $(checkbox)
				.closest(".dt-row")
				.find(".dt-cell__content")
				.map(function () {
				  return $(this).text().trim();
				})
				.get();
			  var member_code = rowData[2];
			  var ceo_name = rowData[5];
			  var committees = rowData[6];
			  var export_value_in_egp = rowData[7];
			  var export_value_in_usd = rowData[8];
			  var export_volume = rowData[9];
			  var governorate = rowData[10];
			  var customer_status = rowData[11];
			  var ceo_mobile = rowData[12];
			  var email = rowData[13];
			  console.log("EMAI", export_volume);
			  ///////////////////////
			  selected_rows.push({
				member_code: member_code,
				ceo_name: ceo_name,
				committees: committees,
				export_value_in_egp: export_value_in_egp,
				export_value_in_usd: export_value_in_usd,
				export_volume: export_volume,
				governorate: governorate,
				customer_status: customer_status,
				ceo_mobile: ceo_mobile,
				email: email,
			  });
			  //////////////////////////
			}
		  });
		// for (let row of selected_rows) {
		frappe.call({
		  method: "frappe.client.insert",
		  args: {
			doc: {
			  doctype: "Foreigner  Affairs  Opportunities",
			  member_code: member,
			  ceo_name: name_of_the_cioowner_of_the_company,
			  committee: committee_name,
			  governorate: territory,
			  customer_status: custom_customer_status,
			  member_info: selected_rows,
			},
		  },
		  callback: function (r) {
			console.log(r.message);
			console.log(r.message.name);
			frappe.set_route(
			  "Form",
			  "Foreigner  Affairs  Opportunities",
			  r.message.name
			);
		  },
		});
  
		//}
		/////////////
	  });
	},
  };