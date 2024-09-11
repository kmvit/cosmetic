document.addEventListener('DOMContentLoaded', function() {
    function updateParameterFields() {
        var paramType = document.querySelector('#id_parameter option:checked').getAttribute('data-param-type');
        var valueStrField = document.querySelector('.field-value_str');
        var valueIntField = document.querySelector('.field-value_int');
        var valueMinField = document.querySelector('.field-value_min');
        var valueMaxField = document.querySelector('.field-value_max');

        valueStrField.style.display = 'none';
        valueIntField.style.display = 'none';
        valueMinField.style.display = 'none';
        valueMaxField.style.display = 'none';

        if (paramType === 'str') {
            valueStrField.style.display = 'block';
        } else if (paramType === 'int') {
            valueIntField.style.display = 'block';
        } else if (paramType === 'range') {
            valueMinField.style.display = 'block';
            valueMaxField.style.display = 'block';
        }
    }

    var parameterSelect = document.querySelector('#id_parameter');
    parameterSelect.addEventListener('change', updateParameterFields);

    // Обновляем все опции параметров, добавляя атрибут `data-param-type`
    fetch('/admin/your_app_name/parameter/').then(response => response.json()).then(data => {
        data.forEach(function(parameter) {
            var option = document.querySelector(`#id_parameter option[value="${parameter.id}"]`);
            if (option) {
                option.setAttribute('data-param-type', parameter.param_type);
            }
        });
        updateParameterFields();
    });

    updateParameterFields();
});
