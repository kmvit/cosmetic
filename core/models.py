from django.db import models


class Property(models.Model):
    """
    Модель свойств косметических средств.
    """
    name = models.CharField(max_length=255, verbose_name="Название свойства")
    order = models.PositiveIntegerField(
        verbose_name="Порядок использования")
    program_types = models.ManyToManyField('ProgramType',
                                           related_name="properties",
                                           verbose_name="Типы программы")

    class Meta:
        verbose_name = 'Свойства'
        verbose_name_plural = "Свойства"

    def __str__(self):
        return self.name


from django.db import models


class Category(models.Model):
    """
    Категории
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Категория")

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Модель косметики
    """
    name = models.TextField(verbose_name="Название")
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 blank=True, null=True,
                                 related_name='products', verbose_name="Категория")
    article_number = models.PositiveIntegerField(verbose_name="Артикул")
    properties = models.ManyToManyField(Property, verbose_name="Свойства")
    frequency_of_use = models.PositiveIntegerField(
        default=1, verbose_name="Частота использования (в днях)"
    )

    def __str__(self):
        return f'{self.name}({self.article_number})'

    class Meta:
        verbose_name = "Косметика"
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
        verbose_name = "Параметры"
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
                                    null=True,
                                    verbose_name="Значения от")  # Для хранения минимального значения диапазона
    value_max = models.IntegerField(blank=True,
                                    null=True,
                                    verbose_name="Значение до")  # Для хранения максимального значения диапазона

    class Meta:
        verbose_name = "Значение"
        verbose_name_plural = "Значения параметров"
        ordering = ['value_str', 'value_int', 'value_min']

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


class ProgramType(models.Model):
    """
    Тип программы
    """
    name = models.CharField(max_length=50,
                            verbose_name="Название программы")
    time_to_send = models.TimeField(
        verbose_name="Время отправки программы")

    class Meta:
        verbose_name = "Тип программы"
        verbose_name_plural = "Тип программы"

    def __str__(self):
        return self.name


class Program(models.Model):
    """
    Модель программы
    """
    user_id = models.CharField(max_length=100,
                               verbose_name="ID пользователя из чата")
    program_type = models.ForeignKey(ProgramType, on_delete=models.CASCADE,
                                     verbose_name="Тип программы")
    products = models.ManyToManyField(Product,
                                      verbose_name="Продукты программы")
    start_date = models.DateField(auto_now_add=True,
                                  verbose_name="Дата старта программы")
    duration = models.PositiveIntegerField(default=100,
                                           verbose_name="Длительность программы в днях")

    class Meta:
        verbose_name = "Программы"
        verbose_name_plural = "Программы"

    def __str__(self):
        return f'user id-{self.user_id} тип программы-{self.program_type}'


class SkincareProgram(models.Model):
    """
    Модель для отслеживания программ ухода.
    """
    user_id = models.PositiveIntegerField(
        verbose_name="ID пользователя в боте")
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                verbose_name="Продукт")
    last_sent = models.DateField(null=True, blank=True,
                                 verbose_name="Последняя отправка")
    program_type = models.CharField(
        max_length=10, choices=(("morning", "Утро"), ("evening", "Вечер")),
        verbose_name="Тип программы"
    )

    def __str__(self):
        return f"{self.user_id} - {self.product.name} - {self.program_type}"
