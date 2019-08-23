from odoo import models, _

class StockGenericReport(models.AbstractModel):
    _name = 'stock.generic.report'
    _inherit = 'generic.report'

    filter_warehouses = True
    filter_product = True
    filter_partner = False
    filter_operation_types = True

    def _get_report_name(self):
        return _('Stock General Report')

    def _get_custom_templates(self):
        return {
            'search_template': 'xb_stock_reports.search_template',
        }

    def _get_filter_warehouses(self):
        return self.env['stock.warehouse'].search([('company_id', 'in', self.env.user.company_ids.ids or [self.env.user.company_id.id])], order="company_id, name")

    def _get_warehouses(self):
        warehouses = []
        previous_company = False
        for wh in self._get_filter_warehouses():
            if wh.company_id != previous_company:
                warehouses.append({'id': 'divider', 'name': wh.company_id.name})
                previous_company = wh.company_id
            warehouses.append({'id': wh.id, 'name': wh.name, 'code': wh.code, 'selected': False})
        return warehouses

    def _merge_previous_options(self, options, previous_options):
        if options.get('warehouses'):
            options['warehouses'] = self._get_warehouses()
        return super(StockGenericReport, self)._merge_previous_options(options, previous_options)

    def _build_options(self, previous_options=None):
        if self.filter_product:
            self.filter_product_ids = []
            self.filter_product_categories = []
        if self.filter_operation_types:
            self.filter_picking_type_ids = []
        return super(StockGenericReport, self)._build_options(previous_options=previous_options)

    def _update_options_searchview_dict(self, options, searchview_dict):
        """
        Split from get_report_informations to update filter state when re-render.
        You must mutable params
        """
        super(StockGenericReport, self)._update_options_searchview_dict(options, searchview_dict)
        searchview_dict['search_template_object'] = "xb_stock_reports.search_template_object"
        if options.get('product'):
            options['selected_products'] = [dict(id=product_id, name=product_name) for product_id, product_name in self.env['product.product'].browse(options['product_ids']).name_get()]
            options['selected_product_categories'] = [dict(id=categ_id, name=categ_name) for categ_id, categ_name in self.env['product.category'].browse(options['product_categories']).name_get()]
        if options.get('operation_types'):
            options['selected_operation_types'] = [dict(id=type_id, name=name) for type_id, name in self.env['stock.picking.type'].browse(options['picking_type_ids']).name_get()]

    def _set_context(self, options):
        ctx = super(StockGenericReport, self)._set_context(options)
        if options.get('warehouses'):
            ctx['warehouse_ids'] = [j.get('id') for j in options.get('warehouses') if j.get('selected')]
        if options.get('operation_types'):
            ctx['picking_type_ids'] = self.env['stock.picking.type'].browse(options['picking_type_ids'])
        if options.get('product_ids'):
            ctx['product_ids'] = self.env['product.product'].browse(options['product_ids'])
        if options.get('product_categories'):
            ctx['product_categories'] = self.env['product.product'].browse(options['product_categories'])
        return ctx

    def _get_select_partners(self):
        return [(partner.id, partner.name) for partner in self.env['res.partner'].search([])]
    
    def _get_select_partner_categories(self):
        return [(category.id, category.name) for category in self.env['res.partner.category'].search([])] or False

    def get_product_auto_complete(self, query, options):
        return [], False
    
    def get_operation_types_auto_complete(self, query, options):
        if options.get('warehouses'):
            warehouse_ids = [j.get('id') for j in options.get('warehouses') if j.get('selected')]
            if warehouse_ids:
                return [('warehouse_id', 'in', warehouse_ids)], False
        return [], False