import {OpenResponse, DataResponse, AcknowledgementResponse} from "./responses.js";

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
        "acknowledgement": AcknowledgementResponse
    }
    
    constructor (path) {
        this.#id = this.#generateID();
        this.connect(path)
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

    connect = (path) => {
        this.#socket?.close()
        
        const url = this.#build_websocket_url(path);
        this.#socket = new WebSocket(url);
        this.#socket.onmessage = this.#handleMessage;
        this.#socket.onopen = this.#handleOpen;
        this.#socket.onclose = this.#handleClose;
        this.#socket.onerror = this.#handleError;
    }

    /**
     *
     * @param event {MessageEvent}
     */
    #handleMessage = (event) => {
        debugger;
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

document.YanvClient = YanvClient;