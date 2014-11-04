from openerp.osv import fields,osv,orm
from openerp.tools.translate import _


class product_product(osv.osv):
    _inherit='product.product'
    _description='Product Fields'
    
    _columns = {
                'product_width':fields.float(string = 'Product Width'),
                'product_height':fields.float(string = 'Product Height'),
                }