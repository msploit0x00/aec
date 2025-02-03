// Copyright (c) 2024, ds and contributors
// For license information, please see license.txt

frappe.ui.form.on('Exhibitions Annual Plan', {
 
	refresh: function(frm) {
		if (frm.doc.workflow_state === 'Approved') {
      let status = []
    
    
      frm.add_custom_button(__('Send to Newsletters'),function(){
        status = []
        let active = frm.doc.active,
        in_active  = frm.doc.inactive,
        suspended = frm.doc.suspended;
        active = (active === 1) ? "active" : "";
        in_active = (in_active === 1) ? "Inactive" : "";
        suspended = (suspended === 1) ? "Suspended" : "";
        status.push(active,in_active,suspended);

        frm.doc.committees.map(AC => {
          console.log("committee is :",AC.the_commission)
          console.log("status IS :",status)
        frm.call({
          method: "get_contact_exhibition",
          args:{
            committee:AC.the_commission,
            status:status,
            name:frm.doc.name,
            docname:frm.doc.doctype
          },callback:function(response){
            console.log("Response",response.message)
            if (response){
              frappe.set_route('Form','Customer Newsletter',response.message.name)
            }

          }
        })
        })
      })
		}
	},


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
