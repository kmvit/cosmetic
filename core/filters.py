from django_filters import rest_framework as filters
from django_filters.widgets import CSVWidget

from .models import Product, ParameterValue

from django_filters import rest_framework as filters
from .models import Product, Parameter, ParameterValue


class DynamicProductFilter(filters.FilterSet):
    """
    Фильтр по продукции
    """

    class Meta:
        model = Product
        fields = []

    def filter_queryset(self, queryset):
        """
        Переопределяем метод для фильтрации по всем параметрам, переданным в запросе.
        """
        for param_name, param_value in self.data.items():
            if param_name == 'parameter':  # пропускаем ключ "parameter"
                continue
            queryset = self.filter_by_parameter(queryset, param_name,
                                                param_value)
        return queryset

    def filter_by_parameter(self, queryset, parameter_name, parameter_value):
        """
        Фильтрация продукции по одному параметру и его значению.
        """
        # Находим параметр по имени
        try:
            parameter = Parameter.objects.get(name=parameter_name)
        except Parameter.DoesNotExist:
            return queryset  # Если параметр не найден, возвращаем исходный queryset

        # Фильтруем значения параметра по типу и значению
        if parameter.param_type == 'str':
            parameter_values = ParameterValue.objects.filter(
                parameter=parameter,
                value_str__iexact=parameter_value
            )
        elif parameter.param_type == 'int':
            try:
                int_value = int(parameter_value)
            except ValueError:
                return queryset  # Если значение не может быть преобразовано в число, пропускаем этот фильтр
            parameter_values = ParameterValue.objects.filter(
                parameter=parameter,
                value_int=int_value
            )
        elif parameter.param_type == 'range':
            try:
                int_value = int(parameter_value)
            except ValueError:
                return queryset  # Если значение не может быть преобразовано в число, пропускаем этот фильтр
            parameter_values = ParameterValue.objects.filter(
                parameter=parameter,
                value_min__lte=int_value,
                value_max__gte=int_value
            )
        else:
            return queryset  # Если тип параметра не поддерживается, возвращаем исходный queryset

        # Получаем ID продуктов, которые связаны с найденными значениями параметров
        filtered_ids = parameter_values.values_list('products__id', flat=True)

        # Возвращаем отфильтрованный queryset
        return queryset.filter(id__in=filtered_ids)