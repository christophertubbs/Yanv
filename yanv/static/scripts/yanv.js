import {closeAllDialogs, openDialog} from "./utility.js";
import {AcknowledgementResponse, DataResponse, OpenResponse} from "./responses.js";
import {DatasetView} from "./views/metadata.js";
import {BooleanValue, ListValue, ListValueAction} from "./value.js";

const PREVIOUS_PATH_KEY = "previousPath";

function initializeBackingVariables() {
    const connected = BooleanValue.True;
    connected.onUpdate(socketIsConnected);

    Object.defineProperty(
        yanv,
        "connected",
        {
            get() {
                return connected.isTrue;
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

    Object.defineProperty(
        yanv,
        "datasets",
        {
            value: new ListValue(
                [],
                handleDatasetAddition,
                handleDatasetRemoval,
                toggleContentLoadStatus
            ),
            enumerable: true
        }
    )
}

async function initializeClient() {

    const client = new yanv.YanvClient();

    client.addHandler("open", () => yanv.connected = true);
    client.addHandler("closed", () => yanv.connected = false);
    client.addHandler("load", dataLoaded);
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
    await yanv.client.connect("ws");
}


/**
 *
 * @param event {ListValueEvent}
 */
function handleDatasetAddition(event){
    if (event.action === ListValueAction.ADD) {
        if (Array.isArray(event.modifiedValue)) {
            event.modifiedValue.forEach((response) => addDatasetView(response));
        }
        else {
            addDatasetView(event.modifiedValue)
        }
    }
}

/**
 *
 * @param event {ListValueEvent}
 */
function handleDatasetRemoval(event) {
    if (event.action !== ListValueAction.DELETE) {
        return
    }

    const dataToRemove = Array.isArray(event.modifiedValue) ? event.modifiedValue : [event.modifiedValue];

    dataToRemove.forEach((response) => {
        const data_id = response.data_id;
        const containerSelector = `#${data_id}`;
        const tabSelector = `#${data_id}-tab`;
        $(containerSelector).remove();
        $(tabSelector).remove();
    })

}
/**
 *
 * @param response {DataResponse}
 */
function dataLoaded(response) {
    if(!yanv.datasets.exists((dataResponse) => dataResponse.data_id === response.data_id)) {
        yanv.datasets.push(response);
    }
    else {
        console.warn(`${response.data.name} has already been loaded`);
    }
}

function toggleContentLoadStatus() {
    const isEmpty = yanv.datasets.isEmpty();

    const contentToShow = $(isEmpty ? "#no-content-block" : "#content");
    const contentToHide = $(isEmpty ? "#content" : "#no-content-block");

    contentToShow.show();
    contentToHide.hide();
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
    try {
        const view = new DatasetView(payload);
        view.render("#content", "#content-tabs");
    } catch (e) {
        console.error(e);
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
    initializeBackingVariables();
    initializeModals();
    $("#loading-progress-bar").progressbar({value: false});
    $("button").button();
    $("#content").tabs();
    toggleContentLoadStatus();

    Object.defineProperty(
        yanv,
        "refreshTabs",
        {
            value: () => {
                const tabsView = $("#content").tabs();
                tabsView.tabs("refresh");
                tabsView.off("click");
                tabsView.on("click", "span.ui-icon-close", function() {
                    yanv.removeData(this.dataset.data_id);
                });
            },
            enumerable: true
        }
    );

    Object.defineProperty(
        yanv,
        "removeData",
        {
            value: (data_id) => {
                const responseIndex = yanv.datasets.findIndex((response) => response.data_id === data_id);

                if (responseIndex >= 0) {
                    yanv.datasets.removeAt(responseIndex);
                }
            }
        }
    )

    initializeOpenPath()
    $("#close-loading-modal-button").on("click", closeLoadingModal);
    $("#load-button").on("click", launchLoadDialog);

    await initializeClient();
}

function removeTab(removalEvent) {

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