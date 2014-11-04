from openerp.addons.base.ir.ir_cron import ir_cron
from openerp.tools.translate import _
import logging
from openerp.osv import fields, osv

from openerp import netsvc

_logger = logging.getLogger(__name__)

def str2tuple(s):
    return eval('tuple(%s)' % (s or '')) 
                
class ir_cron(ir_cron):
    
    
    def gsp_callback(self, cr, uid, model_name, method_name, args, job_id):
        """ Run the method associated to a given job

        It takes care of logging and exception handling.

        :param model_name: model name on which the job method is located.
        :param method_name: name of the method to call when this job is processed.
        :param args: arguments of the method (without the usual self, cr, uid).
        :param job_id: job id.
        """
        args = str2tuple(args)
        model = self.pool.get(model_name)
        if model and hasattr(model, method_name):
            method = getattr(model, method_name)
            try:
                log_depth = (None if _logger.isEnabledFor(logging.DEBUG) else 1)
                netsvc.log(_logger, logging.DEBUG, 'cron.object.execute', (cr.dbname,uid,'*',model_name,method_name)+tuple(args), depth=log_depth)
                if _logger.isEnabledFor(logging.DEBUG):
                    start_time = time.time()
                if model_name == 'crm.phonecall'.decode("utf-8") and method_name == 'scheduler_phonecall'.decode("utf-8") or model_name == "crm.meeting".decode("utf-8") and method_name == 'scheduler_meeting'.decode("utf-8"):
                    if args and (args[0] == 'm' or args[0] == 'p') :
                        method(cr,uid,job_id,*args)
                else:
                    method(cr, uid, *args)
                if _logger.isEnabledFor(logging.DEBUG):
                    end_time = time.time()
                    _logger.debug('%.3fs (%s, %s)' % (end_time - start_time, model_name, method_name))
            except Exception, e:
                self._handle_callback_exception(cr, uid, model_name, method_name, args, job_id, e)
                
    ir_cron._callback=gsp_callback
    
    
    