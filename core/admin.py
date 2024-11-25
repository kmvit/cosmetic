from django.contrib import admin
from django import forms
from .models import Product, Parameter, ParameterValue, Property, Program, \
    ProgramType, Category


# Кастомная форма для модели ParameterValue
class ParameterValueForm(forms.ModelForm):
    class Meta:
        model = ParameterValue
        fields = '__all__'

    class Media:
        js = (
            'admin/js/custom_parametervalue.js',)  # Подключаем наш кастомный JS


class ParameterValueAdmin(admin.ModelAdmin):
    form = ParameterValueForm
    list_display = ('parameter', 'get_value', 'get_products')
    list_filter = ('products', 'parameter')
    filter_horizontal = ('products',)
    fieldsets = (
        ('1 Выбор косметики', {
            'fields': ('products',)
        }),
        ('1 Выбор параметра', {
            'fields': ('parameter',)
        }),
        ('2 Если значение параметра число', {
            'fields': ('value_int',),
            "classes": ["collapse"]
        }),
        ('3 Если значение параметра строка', {
            'fields': ('value_str',),
            "classes": ["collapse"],
        }),
        ('4 Если значение параметра числа от и до', {
            'fields': ('value_min', 'value_max'),
            "classes": ["collapse"]
        }),
    )

    def get_products(self, obj):
        return ", ".join([product.name for product in obj.products.all()])

    get_products.short_description = 'Products'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'parameter':
            field.queryset = Parameter.objects.all()

            # Обновляем поле выбора параметра, чтобы включить `data-param-type` для каждого параметра
            field.widget.attrs['data-param-type'] = ''
            field.choices = [
                (param.id, param.name) for param in Parameter.objects.all()
            ]

        return field


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'article_number', 'category']
    search_fields = ['name', 'article_number']
    list_filter = ('category',)


class ProgramAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'program_type']
    search_fields = ['user_id']
    list_filter = ['user_id']


admin.site.register(Product, ProductAdmin)
admin.site.register(Parameter)
admin.site.register(Property)
admin.site.register(ParameterValue, ParameterValueAdmin)
admin.site.register(ProgramType)
admin.site.register(Program, ProgramAdmin)
