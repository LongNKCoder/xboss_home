from odoo import models, _


class AverageCycle(models.AbstractModel):
    _name = 'stock.average.cycle.report'
    _inherit = 'stock.generic.report'

    def _get_report_name(self):
        return _('Average Cycle')
    
    def _get_columns_name(self, options):
        return [
            [
                { 'name': _('Product Code'), 'rowspan': 2 },
                { 'name': _('Product Name'), 'rowspan': 2, 'style': 'width:30%' },
                { 'name': _('UOM'), 'rowspan': 2 },
                { 'name': _('Average'), 'colspan': 2, 'class': 'text-center' },
                { 'name': _('Cost Price'), 'colspan': 2, 'class': 'text-center' },
                { 'name': _('Average Cycle'), 'rowspan': 2 },
                { 'name': _('Average Days'), 'rowspan': 2 },
            ],
            [
                { 'name': False},
                { 'name': False},
                { 'name': False},
                { 'name': _('Quantity'), },
                { 'name': _('Amount'), },
                { 'name': _('Quantity'), },
                { 'name': _('Amount'), },
                { 'name': False},
                { 'name': False},
            ]
        ]
    
    