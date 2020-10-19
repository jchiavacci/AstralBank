from django.contrib import admin
from .models import Item, Category, Expansion, ItemFile

admin.site.register(Category)
admin.site.register(Expansion)
admin.site.register(ItemFile)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('itemId', 'itemName', 'points', 'category', 'expansion', 'updated')

    class NotProcessableListFilter(admin.SimpleListFilter):
        title = 'Item Status'
        parameter_name = 'items'

        def lookups(self, request, model_admin):
            return(
                ('complete', 'Complete Items'),
                ('incomplete', 'Incomplete Items'),
                ('processable', 'Processable Items'),
                ('not_processable', 'Not Processable Items'),
            )

        def queryset(self, request, queryset):
            if self.value() == 'processable':
                return queryset.exclude(points__isnull=True)
            if self.value() == 'not_processable':
                return queryset.filter(points__isnull=True)
            if self.value() == 'incomplete':
                return queryset.filter(itemName__isnull=True) \
                       | queryset.filter(points__isnull=True) \
                       | queryset.filter(category__isnull=True) \
                       | queryset.filter(expansion__isnull=True)
            if self.value() == 'complete':
                return queryset.filter(itemName__isnull=False)\
                    .filter(points__isnull=False)\
                    .filter(category__isnull=False)\
                    .filter(expansion__isnull=False)

    list_filter = (NotProcessableListFilter,)
