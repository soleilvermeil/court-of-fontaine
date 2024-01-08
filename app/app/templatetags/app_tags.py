from django import template

register = template.Library()

def strreplace(value, arg):
    a, b = arg.split('|')
    return value.replace(a, b)


def percentage(value):
    return format(value, "%")

register.filter('strreplace', strreplace)
register.filter('percentage', percentage)