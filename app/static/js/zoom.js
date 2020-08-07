'use strict';

const HEADER_SIZE = 110,
    gridDiv = $('#grid'),
    svgGrid = $('#grid svg'),
    zoomInGrid = $('#zoomInGrid'),
    zoomOutGrid = $('#zoomOutGrid'),
    tooltipZoomOut = $('#tooltipZoomOut');

let scaleGrid = 1;

$(document).ready(() => {
    tooltipZoomOut.tooltip('disable');

    zoomInGrid.click(() => {
        scaleGrid += 0.05;
        checkEnableButtons(scaleGrid, zoomOutGrid);
        scale(gridDiv, scaleGrid);
    });

    zoomOutGrid.click(() => {
        scaleGrid -= 0.05;
        checkEnableButtons(scaleGrid, zoomOutGrid);
        scale(gridDiv, scaleGrid);
    });

    fullScreenBtn.click(toggleFullScreen);
});

const checkEnableButtons = (scale, btnZoomOut, showTooltip = true) => {
    if (scale <= 0.11) {
        btnZoomOut.prop('disabled', true);
        btnZoomOut.addClass('disabled');
        btnZoomOut.focusout();
        tooltipZoomOut.tooltip('enable');
        if (showTooltip) tooltipZoomOut.tooltip('show');
    } else {
        btnZoomOut.prop('disabled', false);
        btnZoomOut.removeClass('disabled');
        tooltipZoomOut.tooltip('disable');
    }
};

const setDefaultScale = () => {
    const maxHeight = $(window).height();
    let tryScale = 1.0;
    let tryHeight = height * tryScale;
    while ((tryHeight + HEADER_SIZE + 50) > maxHeight) {
        tryScale -= 0.05;
        tryHeight = height * tryScale;
        if (scale < 0.15) break;
    }
    scaleGrid = tryScale;
    checkEnableButtons(scaleGrid, zoomOutGrid, false);
    scale(gridDiv, scaleGrid);
};

const scale = (el, scale) => {
    const width = 100 / scale;
    const margin = 50 / scale;
    el.css({
        '-webkit-transform':'scale(' + scale + ')',
        '-moz-transform': 'scale(' + scale + ')',
        '-o-transform': 'scale(' + scale + ')',
        '-ms-transform': 'scale(' + scale + ')',
        'transform': 'scale(' + scale + ')',
        '-webkit-transform-origin': '0 0',
        '-moz-transform-origin': '0 0',
        '-o-transform-origin': '0 0',
        '-ms-transform-origin': '0 0',
        'transform-origin': '0 0',
        'width': width + '%',
        'margin-bottom': margin + 'px'
    })
};

const toggleFullScreen = () => {
    if ((document.fullScreenElement && document.fullScreenElement !== null) ||    
        (!document.mozFullScreen && !document.webkitIsFullScreen)) {

        if (document.documentElement.requestFullScreen) document.documentElement.requestFullScreen();  
        else if (document.documentElement.mozRequestFullScreen) document.documentElement.mozRequestFullScreen();  
        else if (document.documentElement.webkitRequestFullScreen) document.documentElement.webkitRequestFullScreen(Element.ALLOW_KEYBOARD_INPUT);  
  
    } else {  

        if (document.cancelFullScreen) document.cancelFullScreen();
        else if (document.mozCancelFullScreen) document.mozCancelFullScreen();
        else if (document.webkitCancelFullScreen) document.webkitCancelFullScreen();

    }
};
document.addEventListener("fullscreenchange", () => {
    changeFullScreenIcon();
});
  
document.addEventListener("mozfullscreenchange", () => {
    changeFullScreenIcon();
});
  
document.addEventListener("webkitfullscreenchange", () => {
    changeFullScreenIcon();
});

document.addEventListener("msfullscreenchange", () => {
    changeFullScreenIcon();
});

const changeFullScreenIcon = () => {
    if ((document.fullScreenElement && document.fullScreenElement !== null) ||    
        (!document.mozFullScreen && !document.webkitIsFullScreen)) {
            fullScreenBtn.removeClass('full');
        } else {
            fullScreenBtn.addClass('full');
    }
};