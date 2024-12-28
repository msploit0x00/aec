// Copyright (c) 2024, ds and contributors
// For license information, please see license.txt

frappe.ui.form.on('Exhibitions Annual Plan', {
	on_submit: function(frm) {
    let row = "ahmed";
    frm.call({
      method:"create_tranning_annual_reminder",
      args:{row:row},callback:function(response){
        console.log("Annaul tranning reminder",response.message)

      }
    })
	}
  
});
frappe.ui.form.on('Expected Exhibitions', {
	make_exhibitions(frm,cdt,cdn) {
		// your code here
		let row = locals[cdt][cdn];
		frm.call({
      method:"make_exhibitions",
     args:{
        row:row
     },
     callback:function(response){
     console.log("response",response.message.name)
      if (response.message){
        frappe.set_route('Form','Exhibitions',response.message.name)
      }

     }
    })
		
	}
});
