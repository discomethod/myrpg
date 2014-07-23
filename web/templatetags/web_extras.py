from django.template import Library

register = Library()

@register.filter
def range_(value):
    """
    Filter - returns a list containing range made from given value
    Usage (in template):

    <ul>{% for i in 3|get_range %}
      <li>{{ i }}. Do something</li>
    {% endfor %}</ul>

    Results with the HTML:
    <ul>
      <li>0. Do something</li>
      <li>1. Do something</li>
      <li>2. Do something</li>
    </ul>

    Instead of 3 one may use the variable set in the views
    """
    return range(value)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_list_item(list, index):
    return list[index]
