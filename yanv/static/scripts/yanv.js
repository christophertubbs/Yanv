import {closeAllDialogs, openDialog} from "./utility.js";
import {AcknowledgementResponse, DataResponse, OpenResponse} from "./responses.js";
import {DatasetView} from "./views/metadata.js";
import {BooleanValue} from "./value.js";

const PREVIOUS_PATH_KEY = "previousPath";

async function initializeClient() {
    /**
     *
     * @type {YanvClient}
     */
    yanv.client = new yanv.YanvClient();

    /**
     *
     * @type {BooleanValue}
     */
    yanv.connected = BooleanValue.False;
    yanv.connected.onUpdate(socketIsConnected);

    yanv.client.addHandler("open", () => yanv.connected.toTrue);
    yanv.client.addHandler("closed", () => yanv.connected.toFalse);
    yanv.client.addHandler("load", addDatasetView);
    yanv.client.addHandler("error", handleError);

    yanv.client.registerPayloadType("connection_opened", OpenResponse);
    yanv.client.registerPayloadType("data", DataResponse);
    yanv.client.registerPayloadType("acknowledgement", AcknowledgementResponse);
    yanv.client.registerPayloadType("load", DataResponse)

    await yanv.client.connect("ws");
}

function socketIsConnected(wasConnected, isNowConnected) {
    if (wasConnected === isNowConnected) {
        return;
    }

    const hide = isNowConnected ? ".yanv-when-disconnected" : ".yanv-when-connected";
    const show = isNowConnected ? ".yanv-when-connected" : ".yanv-when-connected";

    $(hide).hide();
    $(show).show();
}

function addDatasetView(payload) {
    const view = new DatasetView(payload);
    view.render("#content", "#content-tabs");
    closeLoadingModal();
}

async function handleError(payload) {
    $("#failed_message_type").text(Boolean(payload['message_type']) ? payload["message_type"] : "Unknown")
    $("#failed-message-id").text(payload['message_id']);
    $("#error-message").text(payload['error_message']);
    openDialog("#error-dialog");
}

async function getData(path) {
    const request = new yanv.FileSelectionRequest({path: path})

    /**
     * @type {HTMLSpanElement}
     */
    const filenameSpan = document.getElementById("currently-loading-dataset");
    filenameSpan.innerText = path;
    request.onSend(function() {
        openDialog("#loading-modal");
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
    $(".yanv-modal:not(#load-dialog):not(#loading-modal)").dialog({
        modal: true,
        autoOpen: false
    });

    $("#error-dialog").dialog({
        modal: true,
        autoOpen: false,
        width: "20%"
    });

    $("#loading-modal").dialog({
        modal: true,
        autoOpen: false,
        width: "50%",
        height: 200
    })
}

async function initialize() {
    initializeModals();
    $("#loading-progress-bar").progressbar({value: false});
    $("button").button();
    $("#content").tabs();
    initializeOpenPath()
    $("#close-loading-modal-button").on("click", closeLoadingModal);
    $("#load-button").on("click", launchLoadDialog);

    if (!Object.hasOwn(window, 'yanv')) {
        console.log("Creating a new yanv namespace");
        window.yanv = {};
    }

    await initializeClient();
}

async function loadDataClicked(event) {
    const url = $("input#open-path").val();
    await getData(url);
    localStorage.setItem(PREVIOUS_PATH_KEY, url);
}

document.addEventListener("DOMContentLoaded", async function(event) {
    await initialize();
});

function closeLoadingModal() {
    closeAllDialogs();
}

function launchLoadDialog() {
    const previousPath = localStorage[PREVIOUS_PATH_KEY];

    if (previousPath) {
        $("input#open-path").val(previousPath);
    }

    openDialog("#load-dialog")
}