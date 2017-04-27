from django import template

register = template.Library()


@register.simple_tag
def query_transform(request, **kwargs):
    """Taken from http://stackoverflow.com/a/24658162/2844093
    return a querystring with updated parameter. Useful, for example
    in pagination to change page number without replacing the whole
    query parameters.

    Usage:

    .. code-block:: html+django

        <a href="/path?{% query_transform request a=5 b=6 %}">
    """

    updated = request.GET.copy()
    for k, v in kwargs.items():
        updated[k] = v
    return updated.urlencode()
