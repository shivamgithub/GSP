from openerp.osv import fields,osv,orm
from openerp.tools.translate import _


class sale_order(osv.osv):
    _inherit='sale.order'
    _description='changes in sale'
    
    # function for related opportunity field for relation with the opportunity that created it.
    def _fun_field4(self,cr,uid,ids,name,arg,context=None):
        print "ids in funfield 4",ids
        res={}
        for id in ids:
            res[id]=False
            try:
                origin=self.browse(cr,uid,id).origin
                print "origin",origin
                if origin and origin.lower().find('opportunity') != -1:
                    origin_id=(origin.split(' '))[1]
                    origin_id=int(origin_id)
                    print "origin_id",origin_id
                    crm=self.pool.get('crm.lead').browse(cr,uid,origin_id)
                    print "crm details",crm.ref,crm.ref._name,crm.ref.id
                    if crm.ref and crm.ref._name=='sale.order' and crm.ref.id==id:
                        res[id]=origin_id
                
            except:
                raise  
                print 'error encountered in _fun_field4 in crm_lead.py in gsp module'
            
        return res
    
    _defaults = {
                 'is_manufacture':True
                 }
    _columns={'opportunity':fields.function(_fun_field4,type='many2one',obj='crm.lead',string='Related Opportunity',method=True),
              'is_manufacture':fields.boolean("Manufacture"),
              }
   
    # overriding the action_button_confirm(confirm sale order) method to run the 'mark won' button in the related opportunity
    def action_button_confirm(self, cr, uid, ids, context=None):
        print "in action button confirm"
        try:
            origin=self.browse(cr,uid,ids[0]).origin
            if origin:
                origin_id=(origin.split(' '))[1]
                origin_id=int(origin_id)
                # to check if the opportunity has this sale order in ref
                crm_obj=self.pool.get('crm.lead')
                i=crm_obj.browse(cr,uid,origin_id).ref.id
                stage_id=crm_obj.browse(cr,uid,origin_id).stage_id
                #print "3333333333333333"
                #print "origin id ===========",origin_id
                #print "origin id ===========",type(origin_id)
                #print "i ===================",i
                #print "i ===================",type(i)
                #print "ids of sale orderi in oportunity",ids[0]
                if ids[0]==i and stage_id.probability != 100.00:
                    #print 'opportunity has this sales order'
                    print "action button confirm case mark won"
                    context_new={'stage_type': 'opportunity', 'default_type': 'opportunity', 'default_user_id': uid, 'needaction_menu_ref': 'sale.menu_sale_quotations','uid':uid,'via_button':False}
                    # via button to distinguish when called from button or another method
                    crm_obj.case_mark_won(cr, uid,[origin_id],context_new)
        except:
            raise
            print "error =================================== error in gsp/sale_order.py/def action_button_confirm"        
        return super(sale_order,self).action_button_confirm(cr, uid, ids, context)
        
    # overriding the action_cancel ( cancel sales order) method to run the 'mark won' button in the related opportunity
    def action_cancel(self, cr, uid, ids, context=None):
        print "in action_cancel"
        res=super(sale_order,self).action_cancel(cr, uid, ids, context)
        try:
            origin=self.browse(cr,uid,ids[0]).origin
            #print "origin ==============",origin
            if origin and context.get('create_quotation',True):
                origin_id=(origin.split(' '))[1]
                origin_id=int(origin_id)
                # to check if the opportunity has this sale order in ref
                crm_obj=self.pool.get('crm.lead')
                i=crm_obj.browse(cr,uid,origin_id).ref.id
                stage_id=crm_obj.browse(cr,uid,origin_id).stage_id
                #print "3333333333333333"
                #print "origin id ===========",origin_id
                #print "origin id ===========",type(origin_id)
                #print "i ===================",i
                #print "i ===================",type(i)
                #print "ids of sale orderi in oportunity",ids[0]
                if (ids[0]==i and stage_id.probability != 0.00) or (ids[0]==i and stage_id.probability == 0.00 and stage_id.type != 'opportunity'):
                    #print 'opportunity has this sales order'
                    print "44444444444444444"
                    context_new={'stage_type': 'opportunity', 'default_type': 'opportunity', 'default_user_id': uid, 'needaction_menu_ref': 'sale.menu_sale_quotations','uid':uid,'via_button':False}
                    # via button to distinguish when called from button or another method
                    crm_obj.case_mark_lost(cr, uid,[origin_id],context_new)
        except:
            raise
            print "error =================================== error in gsp/sale_order.py/def action_button_confirm"        
        return res
