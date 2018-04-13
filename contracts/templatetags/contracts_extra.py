from django import template
from ..utils import pseudocolor
import random

register = template.Library()


register.filter('riskcolor', pseudocolor)


@register.simple_tag
def random_tag():
    a = ['Sourcing', 'Industrial', 'Legal', 'Financial', 'Internal']
    return random.choice(a)