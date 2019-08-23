from odoo import models, _

class StockMoveAnalysis(models.Model):
    _name = 'stock.move.analysis.report'
    _inherit = 'stock.generic.report'

    filter_unfold_all = False

    def _get_report_name(self):
        return _('Stock Move Analysis')
    
    def _get_columns_name(self, options):
        return [
            [
                { 'name': _('Product Name'), 'rowspan': 2,},
                { 'name': _('Product Code'), 'rowspan': 2,},
                { 'name': _('UOM'), 'rowspan': 2,},
                { 'name': _('Des. Wh'), 'rowspan': 2 },
                { 'name': _('Des. Location'), 'rowspan': 2 },
                { 'name': _('Src Outgoing'), 'rowspan': 2 },
                { 'name': _('Src Deliveried'), 'rowspan': 2 },
                { 'name': _('Inco   ming'), 'rowspan': 2 },
                { 'name': _('Receipted'), 'rowspan': 2 },
            ],
        ]

    def _get_lines(self, options, line_id=None):

        warehouse_ids = self._context.get('warehouse_ids')
        date_to = self._context.get('date_to')

        Uom = self.env['uom.uom']

        cols = len(self.get_header(options)[-1])
        Product = self.env['product.product']

        Warehouse = self.env['stock.warehouse']
        warehouses = Warehouse.search([])

        Location = self.env['stock.location']
        locations = Location.search([('usage','=','internal')])

        Move = self.env['stock.move']
        moves = Move.search(['&',('state','!=','draft'),('state','!=','cancel')])
        whs = warehouses

        results = []

        if warehouse_ids:
            whs = warehouses.filtered(lambda r: r.id in warehouse_ids)

        for wh in whs:
            column = ['']*8
            results.append({
                'id': 'wh_'  + str(wh.id),
                'name': wh.name,
                'level': 1,
                'unfoldable': True,
                'unfolded': self._need_to_unfold('wh_'  + str(wh.id), options),
                'columns': [{
                    'name': name}
                    for name in column]})

            for location in locations.filtered(lambda x: x.get_warehouse() == wh):
                location_moves = moves.filtered(lambda x: x.location_dest_id.usage == 'internal' and x.location_id == location)

                if location_moves:
                    results.append({
                        'id': 'location_'  + str(location.id),
                        'name': location.name,
                        'parent_id': 'wh_'  + str(wh.id),
                        'level': 2,
                        'unfoldable': True,
                        'unfolded': self._need_to_unfold('location_'  + str(location.id), options),
                    })
                    lines = Move.read_group(['&',('state','!=','draft'),
                    ('state','!=','cancel'),
                    ('location_id','=',location.id)],
                    ['product_id','product_qty','location_dest_id'],
                    ['product_id','location_dest_id'], lazy=False)
                    products_location = []

                    for line in lines:
                        product = Product.browse(line.get('product_id')[0])
                        dest_location = Location.browse(line.get('location_dest_id')[0])
                        if dest_location.usage == 'internal':
                            products_location.append([product,dest_location,line.get('product_qty')])

                    for product in products_location:
                        columns = [
                        product[0].code,
                        product[0].uom_name,
                        product[1].get_warehouse().name,
                        product[1].name,
                        product[2],
                        0,0,0]
                        results.append({
                        'id': 'move_'  + str(range(0,100)),
                        'name': product[0].name,
                        'parent_id': 'location_'  + str(location.id),
                        'level': 3,
                        'columns': [{'name': name}
                        for name in columns]})

        lines = []

        if line_id:
            for line in results:
                if line.get('id') == line_id or line.get('parent_id') == line_id:
                    lines.append(line)
        else:
            lines = results

        return lines
