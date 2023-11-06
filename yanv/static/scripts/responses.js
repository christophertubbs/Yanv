import {Dataset} from "./model.js";

export class OpenResponse {
    constructor (payload) {
        console.log("Connected")
        console.log(payload)
    }
}

export class AcknowledgementResponse {
    messageID;
    message;

    constructor ({messageID, message}) {
        this.messageID = messageID;
        this.message = message;
    }
}

export class DataResponse {
    operation
    messageID;
    /**
     * @member {Dataset}
     */
    data;
    columns;
    rowCount;
    filters;
    data_id

    constructor ({operation, data_id, message_id, data, columns, rowCount, filters}) {
        this.data_id = data_id;
        this.operation = operation;
        this.messageID = message_id;
        this.data = data;
        this.columns = columns;
        this.rowCount = rowCount;
        this.filters = filters;
    }
}

if (!Object.hasOwn(window, "yanv")) {
    window.yanv = {};
}

window.yanv.DataResponse = DataResponse;
window.yanv.AcknowledgementResponse = AcknowledgementResponse;
window.yanv.OpenResponse = OpenResponse;