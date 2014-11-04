openerp.gsp_customizations= function (instance) {
    var _t = instance.web._t;
    var _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    
    instance.web.gsp_customizations = instance.web.gsp_customizations|| {};

    instance.gsp_customizations.sale_order_line = instance.web.form.FormWidget.extend({
    
	    init: function (field_manager, node) {
		    this._super(field_manager, node);
	    },
		
		start:function() {
			 this._super();
			 var self = this;
			 self.field_manager.on("field_changed:is_manufacture",self,function(e){
				 self.field_manager.datarecord.is_manufacture = !self.field_manager.datarecord.is_manufacture ;
			 });
		},
    });
    instance.web.form.custom_widgets.add('sale_order_line', 'instance.gsp_customizations.sale_order_line');

    instance.web.ListView.include({
    	do_add_record:function(){
    		var self = this;
    		try{	
	    		if (!self.dataset.parent_view.datarecord.is_manufacture) {
	                this.$el.find('table:first').show();
	                this.$el.find('.oe_view_nocontent').remove();
	                this.start_edition().then(function(){
	                    var fields = self.editor.form.fields;
	                    self.editor.form.fields_order.some(function(field){
	                        if (fields[field].$el.is(':visible')){
	                            fields[field].$el.find("input").select();
	                            return true;
	                        }
	                    });
	                });
	            }
	            else {
	            	this._super();
	            }
    		}
    		catch(exception){
    			this._super();
    		}
    	}
    });
};
