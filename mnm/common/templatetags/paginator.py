#  Based on: http://www.djangosnippets.org/snippets/73/
#
#  Modified by Sean Reifschneider to be smarter about surrounding page
#  link context.  For usage documentation see:
#
#     http://www.tummy.com/Community/Articles/django-pagination/

from django import template

register = template.Library()


def paginator(context, adjacent_pages=2, page_obj=None, paginator=None):
    """
    To be used in conjunction with the object_list generic view.

    Adds pagination context variables for use in displaying first, adjacent and
    last page links in addition to those created by the object_list generic
    view.

    """
    page_obj = page_obj or context['page_obj']
    paginator = paginator or context['paginator']

    start_page = max(page_obj.number - adjacent_pages, 1)
    if start_page <= 3:
        start_page = 1
    end_page = page_obj.number + adjacent_pages + 1
    if end_page >= paginator.num_pages - 1:
        end_page = paginator.num_pages + 1
    page_numbers = [
        n
        for n in range(start_page, end_page)
        if n > 0 and n <= paginator.num_pages]

    prev = page_obj.previous_page_number() if page_obj.has_previous() else None
    return {
        'page_obj': page_obj,
        'request': context['request'],
        'paginator': paginator,
        'results_per_page': paginator.per_page,
        'page': page_obj.number,
        'pages': paginator.num_pages,
        'page_numbers': page_numbers,
        'next': page_obj.next_page_number() if page_obj.has_next() else None,
        'previous': prev,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'show_first': 1 not in page_numbers,
        'show_last': paginator.num_pages not in page_numbers,
    }


register.inclusion_tag(
    'components/pagination.html', takes_context=True)(paginator)
