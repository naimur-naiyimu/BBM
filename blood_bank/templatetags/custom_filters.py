from django import template
from ..models import Donation

register = template.Library()

@register.filter
def approved_donation(donations):
    return donations.filter(status='approved').first()