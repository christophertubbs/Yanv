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

    get isTrue() {
        return this.#value === true;
    }

    get isFalse() {
        return this.#value === false;
    }

    valueOf() {
        return this.get()
    }

    toString() {
        return this.get()?.toString();
    }
}

const ListValueAction = Object.freeze({
    DELETE: "delete",
    ADD: "add"
});

/**
 * Event data that will be passed when a ListValue is mutated
 */
class ListValueEvent {
    #action
    #index
    #modifiedValue
    #values

    constructor (action, values, index, modifiedValue) {
        this.#action = action;
        this.#values = values;
        this.#index = index;
        this.#modifiedValue = modifiedValue;
    }

    get action() {
        return this.#action;
    }

    get index() {
        return this.#index;
    }

    get values() {
        return this.#values;
    }

    get modifiedValue() {
        return this.#modifiedValue;
    }
}

export class ListValue {

    /**
     * @type {any[]}
     */
    #values = []

    /**
     *
     * @type {((event: ListValueEvent) => any)[]}
     */
    #handlers = []

    /**
     *
     * @param initialValue {any[]|undefined}
     * @param handlers{(event: ListValueEvent) => any}
     */
    constructor (initialValue, ...handlers) {
        if (Array.isArray(initialValue)) {
            this.#values.push(...initialValue);
        }

        for (let handler of handlers) {
            if (typeof handler === 'function') {
                this.#handlers.push(handler);
            }
        }
    }

    get values() {
        return this.#values;
    }

    /**
     *
     * @param event {ListValueEvent}
     */
    #handleUpdate = (event) => {
        for (let handler of this.#handlers) {
            try {
                handler(this.#values);
            }
            catch (e) {
                console.error(e);
            }
        }
    }

    get length() {
        return this.#values.length;
    }

    concat = (other) => {
        return this.#values.concat(other);
    }

    at = (index) => {
        return this.#values.at(index);
    }

    push = (...other) => {
        const action = ListValueAction.ADD;
        const index = this.#values.length;
        const amountChanged = this.#values.push(...other);
        const event = new ListValueEvent(
            action,
            this.#values,
            index,
            other.length === 1 ? other[0] : other
        );
        this.#handleUpdate(event);
        return amountChanged;
    }

    pop = () => {
        const modifiedValue = this.#values.pop();
        const index = this.#values.length;
        const action = ListValueAction.DELETE;
        const event = new ListValueEvent(action, this.#values, index, modifiedValue);
        this.#handleUpdate(event);
        return modifiedValue;
    }

    entries = () => {
        return this.#values.entries();
    }

    filter = (predicate) => {
        return this.#values.filter(predicate)
    }

    map = (callbackFn, thisArg) => {
        return this.#values.map(callbackFn, thisArg);
    }

    reduce = (callbackFn) => {
        return this.#values.reduce(callbackFn);
    }

    values = () => {
        return this.#values.values();
    }

    reverse = () => {
        return this.#values.reverse();
    }

    sort = (compareFn) => {
        return this.#values.sort(compareFn);
    }

    some = (predicate, thisArg) => {
        return this.#values.some(predicate, thisArg);
    }

    slice = (start, end) => {
        return this.#values.slice(start, end);
    }

    splice = (start, deleteCount, ...items) => {
        const splicedData = this.#values.splice(start, deleteCount)
    }

    valueOf() {
        return this.#values;
    }

    toString() {
        return this.#values.toString();
    }
}