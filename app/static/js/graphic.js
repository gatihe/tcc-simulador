'use strict';

const containerWidth = $('#graphic-container').width(),
    graphicWidth = containerWidth - 30,
    legendWidth = $('#infoLegend').width(),
    htmlGridElement = $('#grid'),
    numberColumnsHeaderInput =  $('#numberColumnsHeader'),
    htmlTitleElement = $('#title'),
    legendBadValue = $('#legendBadValue'),
    legendNeutralValue = $('#legendNeutralValue'),
    legendGoodValue = $('#legendGoodValue'),
    legendBadColor = $('#legendBadColor'),
    legendNeutralColor = $('#legendNeutralColor'),
    legendGoodColor = $('#legendGoodColor'),
    emptyState = $('#emptyState'),
    notEmptyState = $('#notEmptyState'),
    currentOrder = $('#currentOrder');

let biggestColWidth = 0,
    biggestRowWidth = 0,
    colors = null,
    dataRange = null,
    svg = null,
    chromaLegend = null,
    rows = null,
    cols = null,
    matrixForReorder = [],
    data = [],
    rowPointers = [],
    colPointers = [],
    rowsToShow = [],
    dataToShow = [],
    rowPointersToShow = [],
    colPointersToShow = [],
    orderBy = {
        algorithm: 'Ordem Inicial',
        column: '',
        row: '',
        colAsc: true,
        rowAsc: true
    },
    arrayColumn,
    distRows,
    distCols;

d3.select('body')
    .append('div')
    .attr('class', 'tip')
    .style('display', 'none');

const margin = { top: 30, bottom: 1, left: 20, right: 50 },
    dim = d3.min([graphicWidth * 0.7, window.innerHeight * 0.7]),
    padding = 0.1,
    legendTop = 15,
    legendHeight = 15;

let legend = { 
        svg: d3.select('#legend')
                .append('svg')
                .attr('width', legendWidth)
                .attr('height', legendHeight + legendTop)
                .append('g')
                .attr('transform', 'translate(' + margin.left + ', ' + legendTop + ')'),
    },
    width = graphicWidth * 0.8,
    height = graphicWidth * 0.8;

const afterDataLoaded = (inputData, fileName, numberColumnsToAppend) => {
    clearGraphicArea();
    resetVariables(fileName);
    resetOrderBy();
    currentOrder.html(getOrderText());

    const matrixFunctionResult = arrayOfObjectsToMatrix(inputData, numberColumnsToAppend);

    const hasDataToDisplay = displayGraphic(
                                matrixFunctionResult.data, 
                                matrixFunctionResult.rowHeaders, 
                                matrixFunctionResult.columnHeaders
                            );
    if (hasDataToDisplay) {
        matrixForReorder = transformToMatrix(rowPointersToShow, colPointersToShow);
        arrayColumn = getColumnsArray(matrixForReorder);
        distRows = reorder.dist()(matrixForReorder);
        distCols = reorder.dist()(arrayColumn);
        adjustLabelsPositions();
        adjustGridSize();
        displayLegend(legend);
    }
};

const getNumberColumnsHeader = () => {
    const n = numberColumnsHeaderInput.val();
    if (Number.isInteger(parseInt(n))) {
        return n;
    }
    return 1;
};

const clearGraphicArea = () => {
    htmlTitleElement.html('');
    clearGraphic();
    d3.select('#legend').select('svg').remove();
};

const clearGraphic = () => {
    d3.select('#grid').select('svg').remove();
};

const resetVariables = (fileName) => {
    resetGraphic();
        
    colors = getColors();

    dataRange = getRange();
    
    legend.svg = d3.select('#legend')
        .append('svg')
        .attr('width', legendWidth)
        .attr('height', legendHeight + legendTop)
        .append('g')
        .attr('transform', 'translate(' + margin.left + ', ' + legendTop + ')');

        
    htmlTitleElement.html(fileName);
    biggestColWidth = 0;
    biggestRowWidth = 0;
    dataToShow = [];
    rowPointersToShow = [];
    colPointersToShow = [];
    resetOrderBy();
    
    chromaLegend = chroma.scale([colors.bad, colors.neutral, colors.good])
        .domain([dataRange.bad, dataRange.neutral, dataRange.good]);
};

const resetGraphic = () => {
    width = graphicWidth * 0.8;
    height = graphicWidth * 0.8;
    svg = d3.select('#grid')
        .append('svg')
        .append('g')
        .attr('transform', 'translate(' + margin.left + ', ' + margin.top + ')');
};

const arrayOfObjectsToMatrix = (data, numToAppend) => {
    let matrix = [],
        row = {},
        colNum = 0,
        colHeaders = [],
        rowHeaders = [],
        rowHeader = '';

    /* Get column headers and create a matrix with the values */
    for (let header in data[0]) {
        if (colNum >= numToAppend) {
            colHeaders.push(header);
        }
        colNum++;
    }

    /* Get row headers and create a matrix with the values */
    for (let rowNum = 0; rowNum < data.length; rowNum++) {
        colNum = 0;
        for (let key in data[rowNum]) {
            row.row = rowNum;
            if (colNum >= numToAppend){
                row.column = colNum - numToAppend ;
                row.value = data[rowNum][key];
                matrix.push(row);
            } else {
                rowHeader += data[rowNum][key] + ' ';
            }
            row = {};
            colNum++;
        }
        rowHeader = rowHeader.trim();
        rowHeaders.push(rowHeader);
        rowHeader = '';
    }
    
    return {
        'columnHeaders': colHeaders,
        'rowHeaders': rowHeaders,
        'data': matrix
    }
};

const getInitialPointers = length => {
    let pointer = [];
    for (let i = 0; i < length; i++) {
        pointer.push(i);
    }
    return pointer;
};

const displayGraphic = (d, r, c, isOrdering = false) => {
    data = d;
    rows = r;
    cols = c;
    if (!isOrdering) {
        orderByDefault();
    }

    if (dataToShow.length === 0) {
        displayEmptyState();
        return false;
    }
    hideEmptyState();

    const colsLength = cols.length,
        rowsLength = rowsToShow.length;

    width = width * colsLength / 30;
    height = height * rowsLength / 30;

    const x = d3.scaleBand()
            .range([0, width])
            .paddingInner(padding)
            .domain(d3.range(1, colsLength + 1)),

        y = d3.scaleBand()
            .range([0, height])
            .paddingInner(padding)
            .domain(d3.range(1, rowsLength + 1)),

        x_axis = d3.axisTop(x).tickFormat((d, i) => {
                return cols[colPointersToShow[i]];
            }),

        y_axis = d3.axisLeft(y).tickFormat((d, i) => {
                return rows[rowPointersToShow[i]];
            });

    svg.append('g')
        .attr('class', 'x axis')
        .call(x_axis);
    
    svg.append('g')
        .attr('class', 'y axis')
        .call(y_axis);

    svg.selectAll('rect')
        .data(dataToShow)
        .enter()
        .append('rect')
        .attr('data-html', 'true')
        .attr('title', d => {
            const value = isOrdering ? findValue(rowPointersToShow[d.row], colPointersToShow[d.column], true) : d.value;
            return rows[rowPointersToShow[d.row]] + '<br/>' + cols[colPointersToShow[d.column]] + '<br/><strong>Nota:</strong> ' + value;
        })
        .attr('x', d => {
            return x(d.column+1);
        })
        .on('mouseover', mouseover)
        .on('mouseleave', mouseleave)
        .attr('y', d => {
            return y(d.row+1);
        })
        .attr('width', x.bandwidth())
        .attr('height', y.bandwidth())
        .style('fill', d => {
            const value = isOrdering ? findValue(rowPointersToShow[d.row], colPointersToShow[d.column], true) : d.value;
            return chromaLegend(value);
        })
        .style('opacity', 1e-6)
        .transition()
        .style('opacity', 1);

    $('g.x  g.tick > text').each(function(i) {
        $(this).click(() => {
            _beforeOrdering();
            setTimeout(() => {
                orderByColumn(i);
                _afterOrdering();
            }, 200);
        });
    });

    $('g.y  g.tick > text').each(function(i) {
        $(this).click(() => {
            _beforeOrdering();
            setTimeout(() => {
                orderByRow(i);
                _afterOrdering();
            }, 200);
        });
    });
    return true;
};

const displayEmptyState = () => {
    emptyState.css('display', 'flex');
    notEmptyState.css('display', 'none');
}

const hideEmptyState = () => {
    emptyState.css('display', 'none');
    notEmptyState.css('display', 'block');
}

const getFilterRowsArray = (rowHeader, rowPointers, filter) => {
    const rowsToShow = [];
    let row = 0;
    for (let i of rowPointers) {
        if (filter.includes(rowHeader[rowPointers[i]])) {
            rowsToShow.push(rowPointers[i]);
            rowPointersToShow.push(++row);
        }
    }
    return rowsToShow;
};

const getFilteredData = (rPointer, cPointer) => {
    const dataToShow = [];
    for (let i = 0; i < rPointer.length; i++) {
        for (let j = 0; j < cPointer.length; j++) {
            dataToShow.push({ 
                row: i,
                column: j,
                value: findValue(rPointer[i], cPointer[j])
            });
        }
    }
    return dataToShow;
};

const adjustLabelsPositions = () => {
    /* Column Labels */
    d3.select('.x.axis')._groups[0][0].childNodes
        .forEach(function(d) {
            const node = d.childNodes[1];
            if (node) {
                const nodeWidth = node.getBBox().width,
                    addX = nodeWidth < 100 ? nodeWidth  : nodeWidth > 150 ? nodeWidth / 1.6 : nodeWidth / 1.8;
                biggestColWidth = biggestColWidth < nodeWidth ? nodeWidth : biggestColWidth;
                d3.select(node)
                    .attr('transform', 'rotate(-60)')
                    .attr('x', addX)
                    .attr('y', -12)
                    .attr('class', 'label');
            }
        });

    /* Row Labels */
    d3.select('.y.axis')._groups[0][0].childNodes
        .forEach(function(d) {
            const node = d.childNodes[1];
            if (node) {
                const nodeWidth = node.getBBox().width;
                biggestRowWidth = biggestRowWidth < nodeWidth ? nodeWidth : biggestRowWidth;
                d3.select(node)
                    .attr('x', -13)
                    .attr('class', 'label');
            }
        });
};

const adjustGridSize = (isOrdering = false) => {
    /* Adjusting grid height and width based on biggest Column and Row Label sizes */
    if (!isOrdering) {
        biggestRowWidth *= 1.5;
        biggestColWidth *= 1.1;
    }
    d3.select('#grid')._groups[0][0].childNodes
        .forEach(function(d) {
            d3.select(d)
                .attr('height', height + margin.top + margin.bottom + biggestColWidth)
                .attr('width', width + margin.left + margin.right + biggestRowWidth);
            d3.select(d.childNodes[0])
                .attr('height', height + margin.top + margin.bottom + biggestColWidth)
                .attr('width', width + margin.left + margin.right + biggestRowWidth)
                .attr('transform', 'translate(' + (margin.left + biggestRowWidth) + ', ' + (margin.top + biggestColWidth) + ')');
        });
};

const findValue = (r, c) => {
    const location = (rowPointers[r] * colPointers.length) + colPointers[c];
    return dataToShow.length > 0 ? dataToShow[location].value : data[location].value;
};

const orderByColumn = colIndex => {
    const cIndex = colPointersToShow[colIndex];
    orderBy.colAsc = orderBy.column === cIndex ? !orderBy.colAsc : true;
    orderBy.column = cIndex;

    const rPointers = rowPointersToShow;
    let willSort = [];
    for (let i = 0; i < rPointers.length; i++) {
        const value = findValue(i, cIndex);
        willSort.push(value);
    }
    rowPointersToShow = sortWithIndexes(willSort, orderBy.colAsc);
};

const orderByRow = rowIndex => {
    const rIndex = rowPointersToShow[rowIndex];
    orderBy.rowAsc = orderBy.row === rIndex ? !orderBy.rowAsc : true;
    orderBy.row = rIndex;

    const cPointers = colPointersToShow;
    let willSort = [];
    for (let i = 0; i < cPointers.length; i++) {
        const value = findValue(rIndex, i);
        willSort.push(value);
    }
    colPointersToShow = sortWithIndexes(willSort, orderBy.rowAsc);
};

const sortWithIndexes = (toSort, isAsc) => {
    let willSort = [...toSort],
        order = [];
    for (let i = 0; i < willSort.length; i++) {
        willSort[i] = [willSort[i], i];
    }
    willSort.sort((left, right) => isAsc ? sortAsc(left[0], right[0]) : sortDesc(left[0], right[0]));
    for (let j = 0; j < willSort.length; j++) {
        order.push(willSort[j][1]);
    }
    return order;
};

const sortAsc = (a, b) => {
    return a - b;
};

const sortDesc = (a, b) => {
    return b - a;
};

// Tooltip Functions
const mouseover = function(d) {
    const row = d.row + 1;
    const column = d.column + 1;

    $(this).tooltip('show');  // Creating tooltip dynamically so it does not create thousands of tooltip at once

    d3.select(this)
        .style('stroke', 'black')
        .style('opacity', 1);
    d3.select('.x.axis .tick:nth-of-type(' + column + ') text')
        .classed('selected', true);
    d3.select('.y.axis .tick:nth-of-type(' + row + ') text')
        .classed('selected', true);
};

const mouseleave = function(d) {
    const row = d.row + 1;
    const column = d.column + 1;

    d3.select(this).style('stroke', 'none');
    d3.select('.x.axis .tick:nth-of-type(' + column + ') text')
        .classed('selected', false);
    d3.select('.y.axis .tick:nth-of-type(' + row + ') text')
        .classed('selected', false);
};

const displayLegend = legend => {
    legend.defs = legend.svg.append('defs'),
    legend.gradient = legend.defs.append('linearGradient').attr('id', 'linear-gradient'),
    legend.stops = [
        { offset: 0, color: colors.bad, value: dataRange.bad },
        { offset: 0.5, color: colors.neutral, value: dataRange.neutral },
        { offset: 1, color: colors.good, value: dataRange.good }
    ];

    legend.gradient.selectAll('stop')
        .data(legend.stops)
        .enter()
        .append('stop')
        .attr('offset', d => {
            return 100 * d.offset + '%';
        })
        .attr('stop-color', d => {
            return d.color;
        });

    legend.svg.append('rect')
        .attr('width', legendWidth)
        .attr('height', legendHeight)
        .style('fill', 'url(#linear-gradient)');
    displayLegendNumbers(legend);
};

const displayLegendNumbers = legend => {
    legend.svg.selectAll('text')
        .data(legend.stops)
        .enter()
        .append('text')
        .attr('x', (d, i) => {
            const position = legendWidth * d.offset,
                maxMult = dataRange.good.toString().length + 28,
                medMult = dataRange.neutral.toString().length + 18,
                mult = i == 2 ? maxMult : medMult;

            return position - i * mult ;
        })
        .attr('dy', -3)
        .style('text-anchor', () => {
            return 'start';
        })
        .text(d => {
            return d.value.toFixed(2);
        }); 
};

const getColors = () => {
    return {
        bad: legendBadColor.val(),
        neutral: legendNeutralColor.val(),
        good: legendGoodColor.val(),
    };
};

const getRange = () => {
    return {
        bad: parseInt(legendBadValue.val()),
        neutral: parseInt(legendNeutralValue.val()),
        good: parseInt(legendGoodValue.val())
    };
};

const isEmpty = obj => {
    for(let key in obj) {
        if(obj.hasOwnProperty(key))
            return false;
    }
    return true;
};

const orderByDefault = () => {
    rowPointers = getInitialPointers(rows.length);
    colPointers = getInitialPointers(cols.length);
    
    rowsToShow = getFilterRowsArray(rowsClasses, rowPointers, getFilteredClasses());

    const isFiltered = rowsToShow.length < rows.length;
    dataToShow = isFiltered ? getFilteredData(rowsToShow, colPointers) : data;
    rowPointersToShow = rowsToShow;
    colPointersToShow = colPointers;
    
    resetOrderBy();
};

const setCustomOrder = () => {
    selectOrder.val('custom');
}

const getOrderTypeTextColumn = isAsc => {
    return isAsc ? '&#8593;' : '&#8595;';
};

const getOrderTypeTextRow = isAsc => {
    return isAsc ? '&#8594;' : '&#8592;';
};

const getOrderText = () => {

    let orderText = '';
    let type = '';

    if (orderBy.column !== '') {
        setCustomOrder();
        type = getOrderTypeTextColumn(orderBy.colAsc);
        orderText += `<strong><span style='font-size: 1.4rem'>${type}</span> Disciplina</strong> ${cols[orderBy.column]}`;
        if (orderBy.row !== '') {
            orderText += ', '
        }
    }

    if (orderBy.row !== '') {
        setCustomOrder();
        type = getOrderTypeTextRow(orderBy.rowAsc);
        orderText += `<strong><span style='font-size: 1.7rem'>${type}</span> Aluno</strong> ${rows[orderBy.row]}`;
    }

    return orderText !== '' ? `${orderBy.algorithm} - ${orderText}` : '';
};

const _beforeOrdering = () => {
    showLoading();
};

const _afterOrdering = () => {
    clearGraphic();
    resetGraphic();
    displayGraphic(data, rows, cols, true);
    adjustLabelsPositions();
    adjustGridSize(true);
    currentOrder.html(getOrderText());
    hideLoading();
};

const transformToMatrix = (rows, cols) => {
    let matrix = [];
    for (let row in rows) {
        let arrayRow = [];
        for (let col in cols) {
            arrayRow.push(parseInt(findValue(row, col)));
        }
        matrix.push(arrayRow);
    }
    return matrix;
};

const resetOrderBy = () => {
    orderBy = {
        algorithm: 'Ordem Inicial',
        column: '',
        row: '',
        colAsc: true,
        rowAsc: true
    };
}
