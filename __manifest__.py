{
    'name': "Stock Reports",
    'depends': ['xb_generic_reports', 'stock'],
    'data': [
        'views/stock_reports.xml',
        'views/stock_in_out_report.xml',
        'views/search_template_view.xml',
        'views/stock_analysis_view.xml',
        'views/stock_move_analysis_view.xml',
    ]
}