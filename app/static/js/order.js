'use strict';

$(document).ready(() => {
    $('#selectOrder').on('change', handleSelectOrderChange);
});

const handleSelectOrderChange = async function() {
    _beforeOrdering();
    const value = $(this).val();
    setTimeout(() => {
        resetOrderBy();
        if (value === 'default') {
            orderByDefault();
        } else if (value === 'leaf') {
            orderBy.algorithm = 'Leaf Order';
            permuteLeafOrder(matrixForReorder);
        }
        _afterOrdering();
    }, 200);
};

const permuteLeafOrder = (matrix) => {
    const olorder = reorder.optimal_leaf_order(),
        rowsPerm = olorder.distanceMatrix(distRows)(matrix),
        colPerm = olorder.distanceMatrix(distCols)(arrayColumn);

    rowPointersToShow = rowsPerm;
    colPointersToShow = colPerm;
};

const getColumnsArray = (matrix) => {
    const array = [];
    const amountOfColumns = matrix[0].length;
    const amountOfRows = matrix.length;
    for (let matrixRow = 0; matrixRow < amountOfColumns; matrixRow++) {
        const column = [];
        for (let index = 0; index < amountOfRows; index++) {
            column.push(matrix[index][matrixRow]);
        }
        array.push(column);
    }
    return array;
};
