function initializeIframeSource(runtime, element) {
    var iframeElement = document.getElementById('xblock-jupyter-viewer-iframe');
    var handlerUrl = runtime.handlerUrl(element, 'xblock_handler_jupyter');
    iframeElement.src = handlerUrl;
}
