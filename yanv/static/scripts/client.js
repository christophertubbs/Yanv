import {Request} from "./requests.js"
import {OpenResponse, DataResponse, AcknowledgementResponse} from "./responses.js";
const print = console.log

function sleep(ms, message) {
    if (message === null || message === undefined) {
        message = "Waiting...";
    }

    console.log(message);
    return new Promise(resolve => setTimeout(resolve, ms));
}

export class YanvClient {
    /**
     *
     * @type {WebSocket|null}
     */
    #socket = null;
    #handlers = {};
    #id = null;
    #payloadTypes = {
        "connection_opened": OpenResponse,
        "data": DataResponse,
        "acknowledgement": AcknowledgementResponse,
        "load": DataResponse
    }
    
    constructor (path) {
        this.#id = this.#generateID();
    }
    
    addHandler = (event, operation, action) => {
        if (!Object.hasOwn(this.#handlers, operation)) {
            this.#handlers[operation] = [];
        }
        
        this.#handlers[operation].push(action);
    }

    getID = () => {
        return this.#id;
    }
    
    #handle = (operation, payload) => {
        if (Object.hasOwn(this.#payloadTypes, operation)) {
            payload = new this.#payloadTypes[operation](payload);
        }

        if (Object.hasOwn(this.#handlers, operation)) {
            this.#handlers[operation].forEach(action => action(payload));
        }
    }

    #generateID = (length) => {
        if (length === null || length === undefined) {
            length = 8;
        }

        const characterSet = "0123456789ABCDEF";
        function getRandomCharacter() {
            const characterIndex = Math.floor(Math.random() * characterSet.length);
            return characterSet[characterIndex];
        }

        let generatedID = "";

        for (let counter = 0; counter < length; counter++) {
            generatedID += getRandomCharacter();
        }

        return generatedID;
    }

    /**
     *
     * @param payload {Request|object}
     */
    send = async (payload) => {
        if (payload instanceof Request) {
            payload = payload.getRawPayload();
        }

        if (!Object.hasOwn(payload, "message_id")) {
            payload['message_id'] = this.#generateID()
        }

        const rawPayload = JSON.stringify(payload, null, 4)

        while (this.#socket.readyState === 0) {
            await sleep(1000);
        }

        this.#socket.send(rawPayload);
    }
    
    sendRawMessage = (message) => {
        const payload = {
            "message_id": this.#generateID(),
            "message": message
        }
        const requestData = JSON.stringify(payload, null, 4);
        this.#socket.send(requestData);
    }
    
    #build_websocket_url = (path) => {
        const location = window.location;
        return `ws://${location.host}/${path}`;
    }

    connect = async (path) => {
        this.#socket?.close()
        
        const url = this.#build_websocket_url(path);
        this.#socket = new WebSocket(url);
        this.#socket.onmessage = this.#handleMessage;
        this.#socket.onopen = this.#handleOpen;
        this.#socket.onclose = this.#handleClose;
        this.#socket.onerror = this.#handleError;

        while (this.#socket.readyState === 0) {
            await sleep(1000);
        }
    }

    /**
     *
     * @param event {MessageEvent}
     */
    #handleMessage = (event) => {
        const payload = event.data;
        console.log(payload);

        try {
            const deserializedPayload = JSON.parse(payload);

            const operation = deserializedPayload.operation;
            this.#handle(operation, deserializedPayload);
        } catch (e) {
            console.log("Could not deserialize message from server");
        }
    }

    #handleError = (event) => {
        debugger;
    }

    #handleOpen = (event) => {
        console.log("Connection opened");
    }

    #handleClose = (event) => {
        console.log("Connection closed");
        this.#socket = null;
    }
}

if (!Object.hasOwn(window, "yanv")) {
    window.yanv = {};
}

window.yanv.YanvClient = YanvClient;