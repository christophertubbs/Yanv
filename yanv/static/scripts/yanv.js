const PREVIOUS_PATH_KEY = "previousPath";

async function initializeClient() {
    /**
     *
     * @type {YanvClient}
     */
    yanv.client = new yanv.YanvClient();

    yanv.client.addHandler("load", closeLoadingModal);
    await yanv.client.connect("ws");
}

async function getData(path) {
    const request = new yanv.FileSelectionRequest({path: path})

    /**
     * @type {HTMLSpanElement}
     */
    const filenameSpan = document.getElementById("currently-loading-dataset");
    filenameSpan.innerText = path;
    request.onSend(function() {
        /**
         * @type {HTMLDialogElement}
         */
        const modal = document.getElementById("loading-modal");
        modal.showModal();
    });

    await yanv.client.send(request);
}

function initializeOpenPath() {
    $("#load-dialog").dialog({
        modal: true,
        autoOpen: false,
        width: "60%",
        height: 150
    })

    const openPathInput = $("input#open-path");

    openPathInput.autocomplete({
        source: "navigate"
    });

    $("#open-dataset-button").on("click", loadDataClicked);
}

function initializeModals() {
    $(".yanv-modal:not(#load-dialog)").dialog({
        modal: true,
        autoOpen: false
    });
}

async function initialize() {
    initializeModals();
    $("#loading-progress-bar").progressbar({value: false});
    $("button").button();
    $("#content").tabs();
    initializeOpenPath()

    if (!Object.hasOwn(window, 'yanv')) {
        console.log("Creating a new yanv namespace");
        window.yanv = {};
    }

    await initializeClient();
}

async function loadDataClicked(event) {
    const url = $("input#open-path").val();
    $("#load-dialog").dialog("close");
    await getData(url);
    localStorage.setItem(PREVIOUS_PATH_KEY, url);
}

document.addEventListener("DOMContentLoaded", async function(event) {
    await initialize();
});

function closeLoadingModal() {
    /**
     * @type {HTMLDialogElement}
     */
    const modal = document.getElementById("loading-modal");
    modal.close();
}

function closeNotImplementedModal() {
    /**
     * @type {HTMLDialogElement}
     */
    const modal = document.getElementById("not-implemented-dialog");
    modal.close();
}

function launchLoadDialog() {
    const previousPath = localStorage[PREVIOUS_PATH_KEY];

    if (previousPath) {
        $("input#open-path").val(previousPath);
    }

    $("#load-dialog").dialog("open")
}