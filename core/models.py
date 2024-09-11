from django.db import models


# class Cosmetic(models.Model):
#     """
#     Модель косметики
#     """
#     name = models.CharField(max_length=255, verbose_name="Название")
#     article_number = models.PositiveIntegerField(verbose_name="Артикул")
#
#     class Meta:
#         verbose_name = "Косметику"
#         verbose_name_plural = "Косметика"
#
#     def __str__(self):
#         return f'{self.name}({self.article_number})'
#
#
# class Metadata(models.Model):
#     name = models.CharField(max_length=100, verbose_name="Название параметра")
#     METADATA_FIELD_TYPE = (
#         ('0', 'Строка'),
#         ('1', 'Число'),
#         ('2', 'От и до'),
#     )
#     field_type = models.CharField(max_length=1, choices=METADATA_FIELD_TYPE,
#                                   default='0',
#                                   verbose_name="Тип значения параметра")
#
#     class Meta:
#         verbose_name = "Параметр"
#         verbose_name_plural = "Параметры"
#
#     def __str__(self):
#         return self.name
#
#
# class Parameter(models.Model):
#     """
#     Параметры косметики
#     """
#     cosmetic = models.ManyToManyField(Cosmetic,
#                                       blank=True,
#                                       verbose_name="Косметическое средство")
#     metadata = models.ForeignKey(Metadata, on_delete=models.CASCADE,
#                                  blank=True, null=True,
#                                  verbose_name="Параметр")
#     value_char = models.CharField(max_length=100, blank=True, null=True,
#                                   verbose_name="Если строка пишем сюда")
#     value_integer = models.IntegerField(default=0, blank=True, null=True,
#                                         verbose_name="Если число пишем сюда")
#     value_less = models.IntegerField(default=0, blank=True, null=True,
#                                      verbose_name="Число от")
#     value_more = models.IntegerField(default=0, blank=True, null=True,
#                                      verbose_name="Число до")
#
#     @property
#     def value(self):
#         if self.metadata.field_type == '0':
#             return self.value_char
#         elif self.metadata.field_type == '1':
#             return self.value_integer
#         elif self.metadata.field_type == '2':
#             return f'{self.value_less} - {self.value_more}'
#         return self.value_char
#
#     class Meta:
#         verbose_name = "Значение"
#         verbose_name_plural = "Значения параметров"
#
#     def __str__(self):
#         return f'{self.metadata.name} {self.value}'


class Product(models.Model):
    """
    Модель косметики
    """
    name = models.CharField(max_length=255, verbose_name="Название")
    article_number = models.PositiveIntegerField(verbose_name="Артикул")

    def __str__(self):
        return f'{self.name}({self.article_number})'

    class Meta:
        verbose_name = "Косметику"
        verbose_name_plural = "Косметика"


class Parameter(models.Model):
    """
    Модель параметра
    """
    PARAMETER_TYPES = [
        ('str', 'Строка'),
        ('int', 'Число'),
        ('range', 'Диапазон'),
        # Добавьте другие типы, если необходимо
    ]

    name = models.CharField(max_length=255, verbose_name="Название")
    param_type = models.CharField(max_length=10, choices=PARAMETER_TYPES,
                                  verbose_name="Тип параметра")

    class Meta:
        verbose_name = "Параметр"
        verbose_name_plural = "Параметры"

    def __str__(self):
        return self.name


class ParameterValue(models.Model):
    """
    Модель значения параметра
    """
    products = models.ManyToManyField(Product, related_name='parameter_values')
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE)

    value_str = models.CharField(max_length=255, blank=True, null=True,
                                 verbose_name="Значение")
    value_int = models.IntegerField(blank=True, null=True,
                                    verbose_name="Значение")
    value_min = models.IntegerField(blank=True,
                                    null=True, verbose_name="Значения от")  # Для хранения минимального значения диапазона
    value_max = models.IntegerField(blank=True,
                                    null=True, verbose_name="Значение до")  # Для хранения максимального значения диапазона

    class Meta:
        verbose_name = "Значение"
        verbose_name_plural = "Значения параметров"

    def get_value(self):
        """Возвращает значение параметра в зависимости от его типа."""
        if self.parameter.param_type == 'str':
            return self.value_str
        elif self.parameter.param_type == 'int':
            return self.value_int
        elif self.parameter.param_type == 'range':
            return f'от {self.value_min} до {self.value_max}'
        else:
            return None

    def __str__(self):
        return f'{self.parameter.name}: {self.get_value()}'

