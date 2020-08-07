'use strict';

$(document).ready(() => {
    const classificationInputs = $('input[name^="classification"]');
    const sidebar = $('#sidebar');

    $('#chkClassification').change(function() {
        enableClassificationInputs(classificationInputs, !this.checked);
    });

    $('#outsideSidebar').click(function () {
        sidebar.collapse('hide');
    });

    const tooltips = $('[data-toggle="tooltip"]');
    tooltips.tooltip({ 'placement': 'top' });

    $('#legendBad, #legendNeutral, #legendGood').colorpicker();
});

const enableClassificationInputs = (inputs, enable) => {
    inputs.each(function() {
        $(this).prop('disabled', enable);
    });
};
