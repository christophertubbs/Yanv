export class OpenResponse {
    constructor (payload) {
        debugger;
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
    messageID;
    data;
    columns;
    rowCount;
    filters;

    constructor ({message_id, data, columns, rowCount, filters}) {
        this.messageID = message_id;
        this.data = data;
        this.columns = columns;
        this.rowCount = rowCount;
        this.filters = filters;
    }
}