frappe.ui.form.on('Service Generator', {
    validate: function(frm) {
        let service_price_list = frm.doc.service_price_list;
        let default_count = 0;
        let default_row = null;
        
        if(!service_price_list){
            frappe.throw(__('Please add price list first'));
        }

        if(service_price_list.length > 0){
        for (let row of service_price_list) {
            if (row.is_default === 1) {
                default_count++;
                default_row = row;
            }

            if (default_count > 1) {
                frappe.throw(__('Only one service price list can be set as default.'));
            }
        }
    }
    }
});

frappe.ui.form.on('Service Price List', {
    before_save: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        
        if (row.is_default) {
        
            frm.doc.service_price_list.forEach(r => {
                if (r.name !== row.name) {
                    r.is_default = 0;
                }
            });

            frm.refresh_field('service_price_list'); 
        }
    }
});
