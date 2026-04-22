from django.contrib import admin
from .models import ChargingStation, StationReview, Charger, RevenueRecord

@admin.register(ChargingStation)
class ChargingStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'operator', 'location', 'status', 'base_rate')
    list_filter = ('status',)
    search_fields = ('name', 'location', 'operator__username')

@admin.register(Charger)
class ChargerAdmin(admin.ModelAdmin):
    list_display = ('charger_id', 'station', 'charger_type', 'status')
    list_filter = ('charger_type', 'status')
    search_fields = ('charger_id', 'station__name')

@admin.register(RevenueRecord)
class RevenueRecordAdmin(admin.ModelAdmin):
    list_display = ('station', 'amount', 'date', 'booking_id')
    list_filter = ('date',)

admin.site.register(StationReview)