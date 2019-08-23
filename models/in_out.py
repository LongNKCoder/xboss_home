from odoo import models, _


class StockInOut(models.AbstractModel):
    _name = 'stock.in.out.report'
    _inherit = 'stock.generic.report'

    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_month'}
    filter_unfold_all = False

    def _get_report_name(self):
        return _('Stock In Out')
    
    def _get_columns_name(self, options):
        return [
            [
                { 'name': _('Name'), 'rowspan': 3},
                { 'name': _('Code'), 'rowspan': 3},
                { 'name': _('UOM'), 'rowspan': 3},
                { 'name': _('TĐ'), 'rowspan': 2, 'colspan': 2, 'class': 'text-center'},
                { 'name': _('PSTK'), 'colspan': 4, 'class': 'text-center'},
                { 'name': _('TC'), 'rowspan': 2, 'colspan': 2, 'class': 'text-center'},
            ],
            [
                { 'name': _('In'), 'colspan': 2, 'class': 'text-center'},
                { 'name': _('Out'), 'colspan': 2, 'class': 'text-center'}
            ],
            [
                { 'name': False, },
                { 'name': False, },
                { 'name': False, },
                { 'name': _('Quantity'), },
                { 'name': _('Amount'), },
                { 'name': _('Quantity'), },
                { 'name': _('Amount'), },
                { 'name': _('Quantity'), },
                { 'name': _('Amount'), },
                { 'name': _('Quantity'), },
                { 'name': _('Amount'), },
            ]
        ]
    
    def _get_lines(self, options, line_id=None):

        if line_id:
            line_id = int(line_id.split('_')[1]) or None

        Product = self.env['product.product']

        date_from = self._context.get('date_from')
        date_to = self._context.get('date_to')

        cols = len(self.get_header(options)[-1])

        product_context = {
            'warehouse': self._context.get('warehouse_ids', False)
        }
        products = Product.with_context(product_context).search([])

        categories = products.mapped('categ_id').sorted(lambda c: c.name or '')

        if line_id:
            categories = categories.filtered(lambda x: x.id == line_id)

        lines = []

        for categ in categories:
            categ_line_id = 'categ_' + str(categ.id)
            lines.append({
                'id': categ_line_id,
                'name': categ.name,
                'level': 2,
                'unfoldable': True,
                'unfolded': self._need_to_unfold(categ_line_id, options),
                'colspan': cols,
            })
            if self._need_to_unfold(categ_line_id, options):
                for product in products.filtered(lambda p: p.categ_id == categ):

                    columns = [product.default_code, product.uom_id.name]
                    begin = product.with_context(to_date=date_from)
                    columns.append(begin.qty_available)
                    columns.append(begin.qty_available * begin.standard_price)

                    in_range = product.with_context(from_date=date_from, to_date=date_to)
                    columns.append(in_range.incoming_qty)
                    columns.append(in_range.incoming_qty * in_range.standard_price)
                    columns.append(in_range.outgoing_qty)
                    columns.append(in_range.outgoing_qty * in_range.standard_price)

                    end = product.with_context(to_date=date_to)
                    columns.append(end.qty_available)
                    columns.append(end.qty_available * end.standard_price)
                    lines.append({
                    'id': product.id,
                    'name': product.name,
                    'parent_id': categ_line_id,
                    'level': 4,
                    'columns': [{
                    'name': name
                    } for name in columns]
                })

        return lines


