from openerp.osv import fields,osv,orm
from openerp.tools.translate import _

class crm_lead(osv.osv):
    _inherit='crm.lead'
    _description='changes in crm'
    
    # functional field to get the expected revenue from the quotation to the opportunity
    # overriding the planned_revenue field...making it a functional field
    def _fun_field3(self,cr,uid,ids,name,arg,context=None):
        res={}
        for id1 in ids:
            res[id1]=0
            #print "000-1-11-",ids
            #print "00000",res
            
            i=self.pool.get('crm.lead').browse(cr,uid,ids[0]).ref.id
            #print "11111",i
            ref1=str(self.pool.get('crm.lead').browse(cr,uid,ids[0]).ref)
            #print "22222",ref1
            if i:
                s=ref1.find('sale.order')
                if(s != -1):
                    a=self.pool.get('sale.order').browse(cr,uid,i)
                    #print "3333",a
                    untaxed=a.amount_untaxed
                    #print "4444",untaxed
                    res[id1]=untaxed
                    #print "555555",res
        return res
                    
        
        

    _columns={
              'planned_revenues':fields.function(_fun_field3,type='float',string='Expected Revenue',store=True,method=True,track_visibility='always'),
              }
    
    def case_mark_lost(self, cr, uid, ids, context=None):
        print "context ==== case mark lost",context
        
        if context.get('via_button',True) and self.browse(cr,uid,ids[0]).ref:
            raise osv.except_osv(_('Warning!'), _('Please cancel the related sales order/quotation to mark the opportunity as lost.'))        
        return super(crm_lead,self).case_mark_lost(cr, uid, ids, context)
    
    def case_mark_won(self, cr, uid, ids, context=None):
        print "context ==== case mark won",context
        
        if context.get('via_button',True) and self.browse(cr,uid,ids[0]).ref:
            raise osv.except_osv(_('Warning!'), _('Please confirm the related the quotation to mark the opportunity as won.'))        
        return super(crm_lead,self).case_mark_won(cr, uid, ids, context)
    
    
        
        
                  
class crm_make_sale(osv.osv):
    """ Make sale  order for crm """

    _inherit = "crm.make.sale"
    
    ###### overiding the method to make quotations form opportunities to change stage_id to 2nd stage
    ###### in type=opportunity
    
    def makeOrder(self, cr, uid, ids, context=None):
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
            print "id of stage=========0980980980",id_stage,seq
            self.pool.get('crm.lead').write(cr,uid,context['active_id'],{'stage_id':id_stage[0]})
        except:
            #raise
            print "error =================================== error in gsp/crm_lead.py/def makeorder"                                
                
        return super(crm_make_sale,self).makeOrder(cr,uid,ids,context)
        
