from openerp.osv import fields,osv,orm
from openerp.tools.translate import _


class product_product(osv.osv):
    _inherit='mrp.workcenter'
    _description='Fields'
    
    _columns = {
                'max_height':fields.float("Maximum Height"),
                'max_width':fields.float("Maximum Width"),
                'edge_space':fields.float('Edge Space')
                }