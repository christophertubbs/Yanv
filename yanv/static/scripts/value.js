/**
 * @typedef {any} Value
 */

export class EventValue {
    static create(initialValue, ...onUpdate) {
        const newValue = new EventValue(initialValue, ...onUpdate);
        return [newValue.get, newValue.set, newValue.onUpdate];
    }

    /**
     * @type {Value}
     */
    #value
    /**
     *
     * @type {((oldValue: Value, newValue: Value) => any)[]}
     */
    #handlers = []

    constructor(initialValue, ...handler) {
        this.#value = initialValue;

        if (handler !== null) {
            this.#handlers.push(...handler);
        }
    }

    /**
     *
     * @param handler {(oldValue: Value, newValue: Value) => any}
     */
    onUpdate = (handler) => {
        this.#handlers.push(handler);
    }

    #handleUpdate = (oldValue, newValue) => {
        for (let handler of this.#handlers) {
            try {
                handler(oldValue, newValue);
            }
            catch (e) {
                console.error(e);
            }
        }
    }

    /**
     *
     * @returns {Value}
     */
    get = () => {
        return this.#value;
    }

    updateValue = (updatedValue) => {
        const oldValue = this.#value;
        this.#value = updatedValue;
        this.#handleUpdate(oldValue, updatedValue);
    }

    /**
     *
     * @param updatedValue {Value}
     */
    set = (updatedValue) => {
        this.updateValue(updatedValue);
    }

    valueOf() {
        return this.get()
    }

    toString() {
        return this.get()?.toString();
    }
}

export class BooleanValue {
    static create(initialValue, ...handler) {
        if (handler === null || handler.length === 0) {
            throw new Error("Update handlers must be passed when creating a new BooleanValue");
        }

        const newValue = new EventValue(initialValue, ...handler);
        return [newValue.get, newValue.set];
    }

    static get True() {
        return new BooleanValue(true);
    };

    static get False() {
        return new BooleanValue(false)
    };

    /**
     * @type {Boolean}
     */
    #value
    /**
     *
     * @type {((oldValue: boolean, newValue: boolean) => any)[]}
     */
    #handlers = []

    constructor(initialValue, ...handler) {
        this.#value = initialValue ?? false;

        if (handler !== null) {
            this.#handlers = this.#handlers.concat(...handler);
        }
    }

    /**
     *
     * @param handler {(oldValue: boolean, newValue: boolean) => any}
     */
    onUpdate = (handler) => {
        this.#handlers.push(handler);
    }

    #handleUpdate = (oldValue, newValue) => {
        for (let handler of this.#handlers) {
            try {
                handler(oldValue, newValue);
            }
            catch (e) {
                console.error(e);
            }
        }
    }

    /**
     *
     * @returns {boolean}
     */
    get = () => {
        return this.#value;
    }

    #updateValue = (updatedValue) => {
        const oldValue = this.#value;
        this.#value = updatedValue;
        this.#handleUpdate(oldValue, updatedValue);
    }

    get toggle() {
        this.#updateValue(!this.#value);
        return this;
    }

    get toTrue() {
        this.#updateValue(true);
        return this;
    }

    get toFalse() {
        this.#updateValue(false);
        return this;
    }

    valueOf() {
        return this.get()
    }

    toString() {
        return this.get()?.toString();
    }
}