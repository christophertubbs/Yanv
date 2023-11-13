async function initializeClient() {
    /**
     *
     * @type {YanvClient}
     */
    yanv.client = new yanv.YanvClient();

    yanv.client.addHandler("load", closeLoadingModal);
    await yanv.client.connect("ws");
}

async function askForData() {
    // FOR TESTING PURPOSES - REMOVE ASAP
    const nc_url = "/Users/christopher.tubbs/PycharmProjects/Yanv/test/resources/test.nc"
    await getData(nc_url)
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

    $("input#open-path").autocomplete({
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
    await getData(url);
}

document.addEventListener("DOMContentLoaded", async function(event) {
    await initialize();
    //await askForData();
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
    /**
     *
     * @type {HTMLDialogElement}
     */
    $("#load-dialog").dialog("open")
}