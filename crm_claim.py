from openerp.osv import fields ,osv ,orm

class crm_claim(osv.osv):
    _name="crm.claim"
    _inherit="crm.claim"
    _description="claim module"
    
    def create(self,cr,uid,vals,context=None):
	id = super(crm_claim,self).create(cr,uid,vals,context)        
	try:
            info = self.pool.get('res.users').read(cr,uid,uid,['lang','tz'],context)
            if context == None: context = {}
            
            context.update({'lang':str(info.get('lang',False) or ''),
                            'tz':str(info.get('tz',False) or ''),
                            'active_ids':[id],
                            'active_id':id,
                            'uid':uid,
                            'active_model':'crm.claim',
                            }) 
            ir_model_data = self.pool.get('ir.model.data') 
            try:
                template_id = ir_model_data.get_object_reference(cr, uid, 'gsp_customizations', 'email_template_edi_claim')[1]
            except ValueError:
                template_id = False
            try:
                compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
            except ValueError:
                compose_form_id = False 
            ctx = context
            ctx.update({
                'default_model': 'crm.claim',
                'default_res_id': id,
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',  
                'compose_form_id':compose_form_id,
                'custom_module':True,
            })
            context = ctx
            wizard_object = self.pool.get('mail.compose.message')
            brw_obj = self.browse(cr,uid,id,context)
            if brw_obj.partner_id and brw_obj.partner_id.email:
                mail_customer = brw_obj.partner_id.id
                wizard_id = wizard_object.create(cr,uid,{'partner_ids':[(4,mail_customer)],
                                                                                 'template_id':template_id,
                                                                                  'composition_mode':'mass_mail',
                                                                                  'res_id':id
                                                                                  },context)
                values = wizard_object.onchange_template_id(cr, uid, id, template_id,'comment','crm.claim',id, context=None)
                wizard_object.write(cr,uid,wizard_id,values['value'],context)
                ctx.update({
                            'wizard_id':wizard_id,
                            })
                wizard_id_list = []
                wizard_id_list.append(wizard_id) 
                wizard_object.send_mail(cr,uid,wizard_id_list,context)
            else:
                return id
        except:
            return id                              
        return id
        
