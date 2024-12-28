// Copyright (c) 2024, ds and contributors
// For license information, please see license.txt

frappe.ui.form.on('Exhibitions', {
	on_submit: function(frm) {
    if (frm.doc.docstatus = 1){
      let status = []
    
    
      frm.add_custom_button(__('Send to Newsletters'),function(){
        status = []
        let active = frm.doc.active,
        in_active  = frm.doc.in_active,
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
	}
});
