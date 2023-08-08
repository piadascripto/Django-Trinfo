from django.contrib import admin
from .models import Order, Tag, Brokerage, Trade

# Register your models here.

admin.site.register(Order)
admin.site.register(Tag)
admin.site.register(Brokerage)
admin.site.register(Trade)