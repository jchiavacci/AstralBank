from django.contrib import admin

from .models import Transaction, TransactionFile
admin.site.register(TransactionFile)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('time', 'character', 'type', 'item', 'quantity', 'processed')


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


    list_filter = (NotProcessedListFilter,)




#doop = Transaction(blha, blah, Character.get(csvName))