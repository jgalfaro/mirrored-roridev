__author__ = 'ender_al'

from decimal import Decimal, InvalidOperation, DecimalException
def checkStringInputType(variables, vtype):
    flag = True

    for v in variables:
        if vtype == "int":
            """Check if variable is int"""
            try:
                int(v)
            except(KeyError, IndexError, TypeError, ValueError):
                flag = False
        elif vtype == "float":
            try:
                float(v)
            except(KeyError, IndexError, TypeError, ValueError):
                flag = False
        elif vtype == "decimal":
            try:
                Decimal(v)
            except(KeyError, IndexError, TypeError, ValueError, InvalidOperation, DecimalException):
                flag = False
    return flag