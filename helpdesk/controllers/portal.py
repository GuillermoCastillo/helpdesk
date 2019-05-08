
from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        values['tickets_count'] = request.env['helpdesk.ticket'].search_count(
            [])
        return values

    @http.route(['/my/tickets', '/my/tickets/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_my_tickets(self, page=1, date_begin=None, date_end=None,
                           sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Ticket = request.env['helpdesk.ticket']
        domain = []

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups('helpdesk.ticket', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin),
                       ('create_date', '<=', date_end)]
        # projects count
        tickets_count = Ticket.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/tickets",
            url_args={'date_begin': date_begin,
                      'date_end': date_end, 'sortby': sortby},
            total=tickets_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        tickets = Ticket.search(
            domain, order=order, limit=self._items_per_page,
            offset=pager['offset'])
        request.session['my_tickets_history'] = tickets.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'tickets': tickets,
            'page_name': 'ticket',
            'archive_groups': archive_groups,
            'default_url': '/my/tickets',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        })
        return request.render("helpdesk.portal_my_tickets", values)
