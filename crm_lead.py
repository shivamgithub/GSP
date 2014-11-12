from openerp.osv import fields,osv,orm
from openerp.tools.translate import _

class crm_lead(osv.osv):
    _inherit='crm.lead'
    _description='changes in crm'
    
    
    #def onchange_ref_id(self,cr,uid,ids,ref,context):
        
    # functional field to get the expected revenue from the quotation to the opportunity
    # overriding the planned_revenue field...making it a functional field
    def _fun_field3(self,cr,uid,ids,name,arg,context=None):
        print " in _fun_field3"
        res={}
        for id1 in ids:
            print " in _fun_field3 id=",id1
            res[id1]=0
            i=self.pool.get('crm.lead').browse(cr,uid,id1)
            if i.ref and i.ref._name=='sale.order':
                a=self.pool.get('sale.order').browse(cr,uid,i.ref.id)
                untaxed=a.amount_untaxed
                print " untaxed",untaxed
                self.write(cr,uid,[id1],{'planned_revenue':untaxed},context)
        return res
    
    def _get_ids(self,cr,uid,ids,context=None):
        print " in _get_ids",ids
        list_of_ids=[]
        '''sale_line=[]
        for id in ids:
            sale_line.append(self.pool.get('sale.order.line').browse(cr,uid,id).order_id)
        print "sale order line sale order",sale_line'''
        for id in ids:
            a=self.pool.get('sale.order').browse(cr,uid,id)
            try:
                origin=a.origin
                print "origin",origin
                if origin and origin.lower().find('opportunity') != -1:
                    origin_id=(origin.split(' '))[1]
                    origin_id=int(origin_id)
                    print "origin_id",origin_id
                    list_of_ids.append(origin_id)
            except:
                raise
                print "error in _get_ids in crm_lead.py in gsp_customizations"
        print "list of ids _get_ids",list_of_ids
        return list_of_ids

    def write(self, cr, uid, ids, vals, context=None):
        print " in write method crm.lead",vals,context
        if vals.get('stage_id') and len(vals)==1:
            crm=self.pool.get('crm.lead').browse(cr,uid,ids[0])
            crm_case_closed_id=self.pool.get('crm.case.stage').search(cr,uid,[('state','=','done')])
            if crm.ref._name=='sale.order' and crm.stage_id.state=='done':
                raise osv.except_osv(_('Warning!'), _('You cannot change the state of opportunity after it has been won.'))
            if crm.ref._name=='sale.order' and crm.stage_id.state=='cancel':
                raise osv.except_osv(_('Warning!'), _('You cannot change the state of opportunity after it has been lost.'))
            if crm.ref._name=='sale.order' and vals['stage_id']==crm_case_closed_id[0]:
                raise osv.except_osv(_('Warning!'), _('Please confirm the related quotation to mark the opportunity as won.'))
            
        return super(crm_lead,self).write(cr, uid, ids, vals, context)

    _columns={
              'planned_revenue1':fields.function(_fun_field3,type='float',string='Expected Revenue',
                store={
                       'sale.order':(_get_ids,['order_line'],100),
                       },
                    help="subtotal from sale order",track_visibility='always'),
              }
    
    def case_mark_lost(self, cr, uid, ids, context=None):
        print " in case mark lost",context,ids
        if context.get('via_button',True) and self.browse(cr,uid,ids[0]).ref:
            raise osv.except_osv(_('Warning!'), _('Please cancel the related sales order/quotation to mark the opportunity as lost.'))        
        return super(crm_lead,self).case_mark_lost(cr, uid, ids, context)
    
    def case_mark_won(self, cr, uid, ids, context=None):
        print " in case mark won",context,ids
        if context.get('via_button',True) and self.browse(cr,uid,ids[0]).ref:
            raise osv.except_osv(_('Warning!'), _('Please confirm the related quotation to mark the opportunity as won.'))        
        return super(crm_lead,self).case_mark_won(cr, uid, ids, context)
    
    
        
        
                  
class crm_make_sale(osv.osv):
    """ Make sale  order for crm """

    _inherit = "crm.make.sale"
    
    ###### overiding the method to make quotations form opportunities to change stage_id to 2nd stage
    ###### in type=opportunity
    
    def makeOrder(self, cr, uid, ids, context=None):
        print " in make order"
        try:
            id_crm_stages=self.pool.get('crm.case.stage').search(cr,uid,[('type','=','opportunity')])
            obj=self.pool.get('crm.case.stage').browse(cr,uid,id_crm_stages)
            seq=[]
            k=0
            #### putting value of all sequence of stages in seq[] to sort
            for i in obj:
                seq.append(i.sequence)
            #### bubble sort
            for l in range(4):
                for j in range(len(seq)-1):
                    if seq[j]>seq[j+1]:
                        k=seq[j]
                        seq[j]=seq[j+1]
                        seq[j+1]=k
            id_stage=self.pool.get('crm.case.stage').search(cr,uid,[('sequence','=',seq[1])])
            self.pool.get('crm.lead').write(cr,uid,context['active_id'],{'stage_id':id_stage[0],'planned_revenue':0.00})
            crm_lead=self.pool.get('crm.lead').browse(cr,uid,context['active_id'])
            print "crm ------",crm_lead
            if crm_lead.ref and crm_lead.ref._name=='sale.order':
                print "actin_cancel"
                context1={'create_quotation':False}
                self.pool.get('sale.order').action_cancel(cr,uid,[crm_lead.ref.id],context1)
        except:
            raise
            print "error =================================== error in gsp/crm_lead.py/def makeorder"  
        print "returning makeorder"      
        return super(crm_make_sale,self).makeOrder(cr,uid,ids,context)
        
