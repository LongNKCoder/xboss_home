from odoo import models, _

class StockAnalysis(models.Model):
    _name = 'stock.analysis.report'
    _inherit = 'stock.generic.report'

    filter_unfold_all = False

    def _get_report_name(self):
        return _('Stock Analysis')
    
    def _get_columns_name(self, options):
        return [
            [
                { 'name': _('Product Name'), 'rowspan': 2, 'style': 'width:30%' },
                { 'name': _('Quantity Available'), 'rowspan': 2 },
                { 'name': _('Quantity Incoming'), 'rowspan': 2 },
                { 'name': _('Quantity Outcoming'), 'rowspan': 2 },
                { 'name': _('Quantity Expected'), 'rowspan': 2 },
            ],
        ]

    def _get_lines(self, options, line_id=None):
        if line_id:
            line_id = int(line_id) or None

        warehouse_ids = self._context.get('warehouse_ids')
        date_to = self._context.get('date_to')

        cols = len(self.get_header(options)[-1])
        Product = self.env['product.product']

        Warehouse = self.env['stock.warehouse']
        warehouses = Warehouse.search([])
        whs = warehouses

        lines = []

        if warehouse_ids:
            whs = warehouses.filtered(lambda r: r.id in warehouse_ids)
            
        if line_id:
            whs = warehouses.filtered(lambda x: x.id == line_id)

        for wh in whs:
            products = Product.with_context(to_date=date_to,warehouse=wh.id).search(['|','|','|',('qty_available','!=',0),('incoming_qty','!=',0),
            ('outgoing_qty','!=',0),('virtual_available','!=',0)])
            qty_available_sum = 0.0 
            incoming_qty_sum = 0.0
            outgoing_qty_sum = 0.0 
            virtual_available_sum = 0.0

            for product in products:
                qty_available_sum += product.qty_available
                incoming_qty_sum += product.incoming_qty
                outgoing_qty_sum += product.outgoing_qty
                virtual_available_sum += product.virtual_available
            sum_column = [qty_available_sum,incoming_qty_sum,outgoing_qty_sum,virtual_available_sum]
            lines.append({
                'id': wh.id,
                'name': wh.name,
                'level': 2,
                'unfoldable': True,
                'unfolded': self._need_to_unfold(wh.id, options),
                'columns': [{
                    'name': name}
                    for name in sum_column]})
                    
            if self._need_to_unfold(wh.id, options):
                for product in products:
                    columns = [product.qty_available,product.incoming_qty,product.outgoing_qty,product.virtual_available]
                    lines.append({
                            'id': product.id,
                            'name': product.name,
                            'parent_id': wh.id,
                            'level': 4,
                            'columns': [{'name': name}
                            for name in columns]})

        return lines