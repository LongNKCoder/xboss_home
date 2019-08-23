from odoo import models, _

from itertools import zip_longest



class StockAgeingReport(models.AbstractModel):
    _name = 'stock.ageing.report'
    _inherit = 'stock.generic.report'

    DEFAULT_GAPS = 30

    filter_gaps = True

    def _build_options(self, previous_options=None):
        if self.filter_gaps:
            units = [('days', _('Days')), ('months', _('Months')), ('years', _('Years'))]
            self.filter_gap_units = [{'id': unit[0], 'name': unit[1], 'selected': False} for unit in units]
            self.filter_gap_value = self.DEFAULT_GAPS
        return super(StockAgeingReport, self)._build_options(previous_options=previous_options)

    
    def _get_report_name(self):
        return _('Stock Ageing')

    
    def _get_gap_ranges(self, options):
        gaps = options.get('gap_value', self.DEFAULT_GAPS)
        range_start = [x * gaps for x in range(5)]
        range_end = [x * gaps for x in range(1, 5)]
        
        return zip_longest(range_start, range_end)

    def _get_columns_name(self, options):
        gap_columns = []
        for start, end in self._get_gap_ranges(options):
            if end:
                gap_columns.append('%s - %s' % (start, end))
            else:
                gap_columns.append('%s +' % start)
        return [
            [
                { 'name': _('Product Code'), 'rowspan': 2 },
                { 'name': _('Product Name'), 'rowspan': 2, 'style': 'width:30%' },
                { 'name': _('UOM'), 'rowspan': 2 },
                *[{'name': name, 'colspan': 2, 'class': 'text-center' } for name in gap_columns],
                { 'name': _('Total Quantity'), 'colspan': 2,'class': 'text-center'}
            ],
            [
                { 'name': False },
                { 'name': False },
                { 'name': False },
                { 'name': _('Quantity'), },
                { 'name': _('Amount'), },
                { 'name': _('Quantity'), },
                { 'name': _('Amount'), },
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
        warehouse_ids = self._context.get('warehouse_ids')
        quant_domain = []

        if warehouse_ids:
            warehouse_ids = self.env['stock.warehouse'].browse(warehouse_ids)
            quant_domain = [('location_id', 'child_of', warehouse_ids.mapped('view_location_id').ids)]
        quants = self.env['stock.quant'].search(quant_domain)
        return []