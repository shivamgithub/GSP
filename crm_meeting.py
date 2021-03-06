from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.addons.base_status.base_state import base_state
import datetime
from openerp import SUPERUSER_ID

class crm_meeting(osv.Model):
    _inherit = "crm.meeting"
    _description = "Scheduler" 
    _columns = {
                'cron_id':fields.many2one('ir.cron',"Associated Cron Job"),
                }

    def delete_cron (self,cr,uid,cron_id,context):
        for i in cron_id:
            if i.get('cron_id',False):
                self.pool.get('ir.cron').unlink(cr,uid,[i.get('cron_id')[0]],context)
        return True
    
    def unlink(self,cr,uid,ids,context):
        cron_id = self.read(cr,uid,ids,['cron_id'],context)
        self.delete_cron(cr,uid,cron_id,context)
        return super(crm_meeting,self).unlink(cr,uid,ids,context)
    
    def write(self,cr,uid,id,vals,context):
        if vals.get('date',False):
            cron_id = self.read(cr,uid,id,['cron_id'],context)
            for i in cron_id:
                cron_id = i.get('cron_id',False) and i.get('cron_id',False)[0]
                if cron_id:
                    self.pool.get('ir.cron').write(cr,uid,[cron_id],{'nextcall':self.calculate_execution_date(vals.get('date',False))},context)
        return super(crm_meeting,self).write(cr,uid,id,vals,context)
    

    def scheduler_meeting(self,cr,uid,id,*args):
        cr.execute("""
        select * from crm_meeting where cron_id = %s
        """%(id))
        phonecall_id = False
        context = {}
        for v in cr.fetchall():
            phonecall_id = v[0]
        
        
        if phonecall_id:
            obj = self.pool.get('crm.meeting').browse(cr,uid,phonecall_id,context)
            if obj.user_id:
                context.update({'lang':obj.user_id.lang or '',
                                'tz':obj.user_id.tz,
                                'active_ids':[phonecall_id],
                                'active_id':phonecall_id,
                                'uid':uid,
                                'active_model':'crm.meeting',
                                }) 
                ir_model_data = self.pool.get('ir.model.data') 
                try:
                    template_id = ir_model_data.get_object_reference(cr, uid, 'gsp_customizations', 'email_template_edi_meeting')[1]
                except ValueError:
                    template_id = False
                try:
                    compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
                except ValueError:
                    compose_form_id = False 
                ctx = context
                ctx.update({
                    'default_model': 'crm.meeting',
                    'default_res_id': phonecall_id,
                    'default_use_template': bool(template_id),
                    'default_template_id': template_id,
                    'default_composition_mode': 'comment',  
                    'compose_form_id':compose_form_id,
                    'custom_module':True,
                })
                context = ctx
                wizard_object = self.pool.get('mail.compose.message')
                wizard_id = wizard_object.create(cr,uid,{'partner_ids':[(4,obj.user_id.partner_id.id)],
                                                                                 'template_id':template_id,
                                                                                  'composition_mode':'comment',
                                                                                  'model':'crm.meeting',
                                                                                  'res_id':phonecall_id
                                                                                  },context)
                values = wizard_object.onchange_template_id(cr, uid, phonecall_id, template_id,'comment','crm.meeting',phonecall_id, context=None)
                wizard_object.write(cr,uid,wizard_id,values['value'],context)
                ctx.update({
                            'wizard_id':wizard_id,
                            })
                wizard_id_list = []
                wizard_id_list.append(wizard_id) 
                wizard_object.send_mail(cr,uid,wizard_id_list,context)
        return True
    
    def calculate_execution_date(self,date):
        date = datetime.datetime.strptime(date,"%Y-%m-%d %H:%M:%S")
        date = date - datetime.timedelta(hours=1)
        date = datetime.datetime.strftime(date,"%Y-%m-%d %H:%M:%S")
        return date
    
    def create(self,cr,uid,vals,context):
        vals_call = {
                     'name':"Meeting reminder for " + vals.get('name',False),
                     'user_id':SUPERUSER_ID,
                     'interval_number':1,
                     'nextcall':self.calculate_execution_date(vals.get('date',False)),
                     'doall':True,
                     'interval_type':"hours",
                     'number_call':1,
                     'model':'crm.meeting',
                     'function': 'scheduler_meeting',
                     'active':True,
                     'priority':1,
                     'args':"('m')",
                     }
        call_id = self.pool.get('ir.cron').create(cr,uid,vals_call,context)
        vals.update({"cron_id":call_id})
        return super(crm_meeting,self).create(cr,uid,vals,context)
    
    
    
    
    
    
