from django import template
from ..utils import pseudocolor

register = template.Library()


register.filter('riskcolor', pseudocolor)