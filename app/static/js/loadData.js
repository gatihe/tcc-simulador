'use strict';

const legendTitle = $('#legendTitle'),
    loading = $('#loading'),
    loadingBackground = $('#loadingBackground'),
    divFilterClasses = $('#filterClass'),
    fullScreenBtn = $('#fullScreen'),
    sidebar = $('#sidebar'),
    selectOrder = $('#selectOrder'),
    infoOrder = $('#infoOrder');

let readerData, fileName, numberColumnsToAppend, loadingText, classColumn,
    filterClasses, rowsClasses = [], oldData, oldFilters, oldColors, oldRange,
    currentData, sidebarToggle;

$(document).ready(() => {
    document.getElementById('fileInput').addEventListener('onmouseover', loadFile);
    sidebar.on('hidden.bs.collapse', generateGraphic);
    sidebar.on('show.bs.collapse', adjustZIndexLess);
});

const adjustZIndexLess = () => {
    fullScreenBtn.css('z-index', '0');
    selectOrder.css('z-index', '0');
    tooltipZoomOut.css('z-index', '0');
    zoomInGrid.css('z-index', '0');
    zoomOutGrid.css('z-index', '0');
};

const adjustZIndexMore = () => {
    fullScreenBtn.css('z-index', '1030');
    selectOrder.css('z-index', '1030');
    tooltipZoomOut.css('z-index', '1030');
    zoomInGrid.css('z-index', '1030');
    zoomOutGrid.css('z-index', '1030');
};

const generateGraphic = async ({ force = false }) => {
    if (!sidebar.hasClass('show')) {
        if (currentData) {
            const currentFilters = getFilteredClasses();
            const currentRange = getRange();
            const currentColors = getColors();

            if (force || oldData !== currentData || !isShallowEqual(oldFilters, currentFilters) || !isShallowEqual(oldColors, currentColors)
            || !isShallowEqual(oldRange, currentRange)) {
                showLoading();
                setTimeout(() => {
                    afterDataLoaded(readerData, fileName, numberColumnsToAppend);
                    $('#selectOrder').val('default');
                    infoOrder.css('display', 'flex');
                    legendTitle.css('display', 'block');
                    zoomInGrid.css('display', 'inline-block');    // zoomInGrid is set in zoom.js
                    zoomOutGrid.css('display', 'inline-block');   // zoomOutGrid is set in zoom.js
                    oldData = currentData;
                    oldFilters = currentFilters;
                    oldRange = dataRange;
                    oldColors = colors;
                    if (!force) setDefaultScale();
                    hideLoading();
                }, 200);
            }
        }
    }
};

const showLoading = () => {
    loading.show();
    loading.removeClass('hiddenLoading');
    loadingBackground.show();
    loadingBackground.removeClass('hiddenLoading');
    adjustZIndexLess();
};

const hideLoading = () => {
    loading.addClass('hiddenLoading');
    loadingBackground.addClass('hiddenLoading');
    loadingBackground.addClass('d-flex');
    adjustZIndexMore();
};

const getFilteredClasses = () => {
    const filteredClasses = [];
    $("input:checkbox[name=class]:checked").each(function(){
        filteredClasses.push($(this).val());
    });
    return filteredClasses;
}

const displayFilterClasses = classes => {
    let html = '';
    for (let classEl of classes) {
        html += `
        <div class="col-sm-12 mb-1">
            <input class="form-check-input" id="chk${classEl}" name="class" type="checkbox" value="${classEl}" checked>
            <label class="form-check-label" for="chk${classEl}">
                ${classEl}
            </label>
        </div>
        `;
    }
    divFilterClasses.html(html);
};

const loadFile = event => {
    const file = event.target.files[0],
    reader = new FileReader();
    reader.addEventListener('load', function() { parseFile(this) });
    if (file) {
        fileName = file.name;
        reader.fileName = file.name;
        reader.fileExtension = file.name.substr(file.name.lastIndexOf('.') + 1);
        reader.readAsDataURL(file);
    }
};

const    getFirstLine = text => {return text.substring(0, text.indexOf("\n") + 1);};
const removeFirstLine = text => {return text.substring(   text.indexOf("\n") + 1);};

const getFilterClasses = (data, colName) => {
    const filter = [];
    rowsClasses = [];
    for (let i = 0; i < data.length; i++) {
        if (filter.indexOf(data[i][colName]) === -1) {
            filter.push(data[i][colName]);
        }
        rowsClasses.push(data[i][colName]);
    }
    return filter;
};

const parseFile = (reader) => {
    if (reader.fileExtension === 'csv') {
        d3.text(reader.result, function(rawData) {
            const dsv = d3.dsvFormat(getFirstLine(rawData));
            rawData                = removeFirstLine(rawData);
            numberColumnsToAppend     = getFirstLine(rawData);
            rawData                = removeFirstLine(rawData);
            classColumn               = getFirstLine(rawData);
            classColumn = classColumn.replace(/(\r\n|\n|\r)/gm, "");
            rawData                = removeFirstLine(rawData);
            readerData = dsv.parse(rawData);

            filterClasses = getFilterClasses(readerData, classColumn);
            displayFilterClasses(filterClasses);
            currentData = rawData;
        });
    }
};

const isShallowEqual = (a, b) => { return JSON.stringify(a) === JSON.stringify(b); };
