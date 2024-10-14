from rest_framework import serializers

from core.models import Product, Parameter, ParameterValue


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для импорта косметики из бд сайта
    """

    class Meta:
        model = Product
        fields = [
            'name',
            'article_number'
        ]


class ParameterValueSerializer(serializers.ModelSerializer):
    """
    Сериализатор для значений параметров продукции.
    """
    parameter = serializers.SlugRelatedField(
        slug_field='name', queryset=Parameter.objects.all()
    )

    class Meta:
        model = ParameterValue
        fields = ['parameter', 'value_str', 'value_int', 'value_min',
                  'value_max']

    def create(self, validated_data):
        """
        Создаем ParameterValue с правильными типами значений.
        """
        parameter = validated_data['parameter']

        if parameter.param_type == 'str':
            return ParameterValue.objects.create(
                parameter=parameter,
                value_str=validated_data.get('value_str', '')
            )
        elif parameter.param_type == 'int':
            return ParameterValue.objects.create(
                parameter=parameter,
                value_int=validated_data.get('value_int', None)
            )
        elif parameter.param_type == 'range':
            return ParameterValue.objects.create(
                parameter=parameter,
                value_min=validated_data.get('value_min', None),
                value_max=validated_data.get('value_max', None)
            )
        return None

    def to_representation(self, instance):
        """
        Переопределяем метод to_representation для удаления полей с null значениями.
        """
        representation = super().to_representation(instance)
        # Удаляем ключи, значения которых равны None
        return {key: value for key, value in representation.items() if
                value is not None}


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для продукции.
    """
    parameter_values = ParameterValueSerializer(many=True)

    class Meta:
        model = Product
        fields = ['name', 'article_number', 'parameter_values']

    # def create(self, validated_data):
    #     """
    #     Создаем продукт с его параметрами.
    #     """
    #     parameter_values_data = validated_data.pop('parameter_values')
    #     product = Product.objects.create(**validated_data)
    #
    #     # Создаем связанные ParameterValue для продукта
    #     for parameter_value_data in parameter_values_data:
    #         parameter_value = ParameterValueSerializer().create(
    #             parameter_value_data)
    #         product.parameter_values.add(parameter_value)
    #
    #     return product
