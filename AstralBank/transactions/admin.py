from django.contrib import admin
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
from rangefilter.filter import DateRangeFilter

from .models import Transaction, TransactionFile
admin.site.register(TransactionFile)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('time', 'character', 'type', 'item', 'quantity', 'processed')
    actions = ['process_items']
    def process_items(self, request, queryset):
        for t in queryset:
            t.process()
    process_items.short_description = 'Process Transactions'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('character__player')
        qs = qs.prefetch_related('item')
        qs = qs.prefetch_related('character')
        return qs


    class NotProcessedListFilter(admin.SimpleListFilter):
        title = 'Show Transactions'
        parameter_name = 'transactions'

        def lookups(self, request, model_admin):
            return(
                ('processed', 'Processed Transactions'),
                ('not_processed', 'Not Processed Transactions'),
            )

        def queryset(self, request, queryset):
            if self.value() == 'processed':
                return queryset.filter(processed=True)
            if self.value() == 'not_processed':
                return queryset.filter(processed=False)


    list_filter = (NotProcessedListFilter,
                   ('character__player', RelatedDropdownFilter),
                   ('time', DateRangeFilter),
                   ('item__expansion', RelatedDropdownFilter),
                   ('item__category', RelatedDropdownFilter))





#doop = Transaction(blha, blah, Character.get(csvName))