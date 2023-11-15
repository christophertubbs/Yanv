import {closeAllDialogs, openDialog} from "./utility.js";
import {AcknowledgementResponse, DataResponse, OpenResponse} from "./responses.js";
import {DatasetView} from "./views/metadata.js";
import {BooleanValue} from "./value.js";

const PREVIOUS_PATH_KEY = "previousPath";

async function initializeClient() {
    /**
     *
     * @type {BooleanValue}
     */
    const contentLoaded = BooleanValue.True;
    contentLoaded.onUpdate(contentHasBeenLoaded);

    Object.defineProperty(
        yanv,
        "contentLoaded",
        {
            get() {
                return contentLoaded;
            },
            set(newValue) {
                if (newValue) {
                    return contentLoaded.toTrue;
                }
                else {
                    return contentLoaded.toFalse;
                }
            },
            enumerable: true
        }
    )

    const connected = BooleanValue.True;
    connected.onUpdate(socketIsConnected);

    Object.defineProperty(
        yanv,
        "connected",
        {
            get() {
                return connected;
            },
            set(newValue) {
                if (newValue) {
                    return connected.toTrue
                }
                return connected.toFalse
            },
            enumerable: true
        }
    )

    const client = new yanv.YanvClient();

    client.addHandler("open", () => yanv.connected.toTrue);
    client.addHandler("closed", () => yanv.connected.toFalse);
    client.addHandler("load", addDatasetView);
    client.addHandler("error", handleError);

    client.registerPayloadType("connection_opened", OpenResponse);
    client.registerPayloadType("data", DataResponse);
    client.registerPayloadType("acknowledgement", AcknowledgementResponse);
    client.registerPayloadType("load", DataResponse)

    Object.defineProperty(
        yanv,
        "client",
        {
            value: client,
            enumerable: true
        }
    )

    yanv.connected = false;
    yanv.contentLoaded = false;
    await yanv.client.connect("ws");
}

function contentHasBeenLoaded(wasLoaded, isNowLoaded) {
    if (wasLoaded === isNowLoaded) {
        return;
    }

    const contentToHide = $(isNowLoaded ? "#no-content-block" : "#content");
    const contentToShow = $(isNowLoaded ? "#content" : "#no-content-block");

    contentToHide.hide();
    contentToShow.show();

    console.log("The content loaded state should now be reflected");
}

function socketIsConnected(wasConnected, isNowConnected) {
    if (wasConnected === isNowConnected) {
        return;
    }

    const contentToHide = $(isNowConnected ? ".yanv-when-disconnected" : ".yanv-when-connected");
    const contentToShow = $(isNowConnected ? ".yanv-when-connected" : ".yanv-when-disconnected");

    contentToHide.hide();
    contentToShow.show();
}

/**
 *
 * @param payload {DataResponse}
 */
function addDatasetView(payload) {
    yanv.contentLoaded = true;
    try {
        const view = new DatasetView(payload);
        view.render("#content", "#content-tabs");
    } catch (e) {
        yanv.contentLoaded = false;
    }
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