from .models import *
from django.db.models import Count
from django.db.models.functions import ExtractDay, ExtractYear, ExtractMonth


def stat_tour_category():
    t = Tour.objects \
              .values('category_id') \
              .annotate(dcount=Count('category_id')) \
              .order_by()
    return t

def stat_tour_all():
    tour_all = Tour.objects \
                .values('name_tour', 'price_of_tour', 'category_id', 'created_date', 'updated_date',) \
                .filter(active=True)

    return tour_all

def report_invoice(month, year=None, day=None):
    tong = 0
    if day:
        invoices = Invoice.objects.annotate(day=ExtractDay('created_date'), month=ExtractMonth('created_date'),
                                            year=ExtractYear('created_date')).values('id', 'total_amount', 'tour_id',
                                                                                     'payer_id', 'day', 'month',
                                                                                     'year', 'status_payment').filter(
            day=day,
            month=month,
            year=year, status_payment=1)
    else:
        invoices = Invoice.objects.annotate(month=ExtractMonth('created_date'),
                                            year=ExtractYear('created_date')).values('id', 'total_amount', 'tour_id',
                                                                                     'payer_id', 'month',
                                                                                     'year', 'status_payment').filter(
            month=month,
            year=year, status_payment=1)

    for i in invoices:
        tong = tong + float(i['total_amount'])

    return tong

