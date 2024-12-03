frappe.ui.form.on('Service Generator', {
    validate: function(frm) {
        let service_price_list = frm.doc.service_price_list || [];
        let default_count = 0;
        let default_row = null;

        
        if (service_price_list.length === 0 && frm.doc.is_free_service == 0) {
            frappe.throw(__('Please add a price list first.'));
        }

        if (service_price_list.length > 0 && frm.doc.is_free_service == 0) {
            for (let row of service_price_list) {
                if (row.is_default === 1) {
                    default_count++;
                    default_row = row;
                }

                if (default_count > 1) {
                    frappe.throw(__('Only one service price list can be set as default.'));
                }
            }
        } else {
            console.log("Done");
        }
    },







    depend_on: function (frm) {
        if (frm.doc.depend_on == 1) {
            frm.set_query('depend_on_doc', function () {
                return {
                    filters: {
                        name: ['in', ['Agriculture Certificate Data', 'Production requirements card']]
                    }
                };
            });
        }
    },





    refresh: function (frm) {
        frm.fields_dict['sales_invoice_print_formats'].grid.get_field('print_format').get_query = function () {
            return {
                filters: {
                    "doc_type": 'Sales Invoice',
                }
            };
        };



        frm.fields_dict['service_request_print_formats'].grid.get_field('print_format').get_query = function () {
            return {
                filters: {
                    "doc_type": 'Service Request',
                }
            };
        };
        



        frm.fields_dict['service_price_list'].grid.get_field('price_list').get_query = function () {
            return {
                filters: {
                    "selling": 1,
                    "enabled": 1,
                }
            };
        };





    }







});

frappe.ui.form.on('Service Price List', {
    before_save: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        
        // if(frm.doc.is_free_service == 0){
        if (row.is_default) {
        
            frm.doc.service_price_list.forEach(r => {
                if (r.name !== row.name) {
                    r.is_default = 0;
                }
            });

            frm.refresh_field('service_price_list'); 
        }

    // }
    }
});
