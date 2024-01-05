from django import template

register = template.Library()

def strreplace(value, arg):
    a, b = arg.split('|')
    return value.replace(a, b)

register.filter('strreplace', strreplace)