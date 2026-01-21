import {Dataset} from "./model.js";

export class OpenResponse {
    constructor (payload) {
        console.log("Connected")
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

export class DataDescriptionResponse {
    /**
     * @member {string}
     */
    operation
    /**
     * @member {string}
     */
    messageID
    /**
     * @member {string}
     */
    container_id
    /**
     * @member {string}
     */
    data_id
    /**
     * @member {string}
     */
    variable
    /**
     * @member {string|null}
     */
    minimum
    /**
     * @member {string|null}
     */
    maximum
    /**
     * @member {string|null}
     */
    mean
    /**
     * @member {string|null}
     */
    median
    /**
     * @member {string|null}
     */
    std
    /**
     * @member {string[]}
     */
    samples
    /**
     * @member {int}
     */
    count

    constructor({data_id, count, minimum, maximum, median, mean, std, samples, variable, messageID, operation}) {
        this.data_id = data_id
        this.count = count
        this.minimum = minimum
        this.maximum = maximum
        this.median = median
        this.std = std
        this.mean = mean
        this.samples = samples
        this.variable = variable
        this.messageID = messageID
        this.operation = operation
    }
}

export class RenderResponse {
    /**
     * @member {string}
     */
    operation
    /**
     * @member {string}
     */
    messageID
    /**
     * @member {string}
     */
    container_id
    /**
     * @member {string}
     */
    markup
    /**
     * @member {"child"|"sibling"}
     */
    position

    constructor({container_id, markup, position, messageID, operation}) {
        this.container_id = container_id
        this.markup = markup
        this.position = position
        this.messageID = messageID
        this.operation = operation
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
    console.log("Creating a new yanv namespace");
    window.yanv = {};
}

window.yanv.DataResponse = DataResponse;
window.yanv.AcknowledgementResponse = AcknowledgementResponse;
window.yanv.OpenResponse = OpenResponse;
window.yanv.DataDescriptionResponse = DataDescriptionResponse;
window.yanv.RenderResponse = RenderResponse;
