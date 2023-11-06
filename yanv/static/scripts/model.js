export class Dimension {
    /**
     * @member {string}
     */
    name
    count
    /**
     * @member {string}
     */
    datatype
    /**
     * @member {string|null|undefined}
     */
    long_name
    /**
     * @member {{string: any}}
     */
    attributes

    constructor ({name, count, datatype, attributes, long_name}) {
        this.name = name;
        this.count = count;
        this.datatype = datatype;
        this.attributes = attributes;
        this.long_name = long_name;
    }
}

export class Variable {
    /**
     * @member {string}
     */
    name
    /**
     * @member {string}
     */
    datatype
    /**
     * @member {number}
     */
    count
    /**
     * @member {Dimension[]}
     */
    dimensions
    /**
     * @member {string|null}
     */
    long_name
    /**
     * @member {string|null}
     */
    units
    /**
     * @member {{string: any}}
     */
    attributes

    constructor ({name, datatype, count, dimensions, long_name, units, attributes}) {
        this.name = name;
        this.datatype = datatype;
        this.count = count;
        this.long_name = long_name
        this.dimensions = dimensions
        this.units = units
        this.attributes = attributes
    }
}

export class Dataset {
    /**
     * @member {Variable[]}
     */
    variables
    /**
     * @member {Dimension[]}
     */
    dimensions
    /**
     * @member {string[]}
     */
    sources
    /**
     * @member {{string: any}}
     */
    attributes

    constructor ({variables, dimensions, sources, attributes}) {
        this.variables = variables;
        this.dimensions = dimensions;
        this.sources = sources;
        this.attributes = attributes;
    }
}

if (!Object.hasOwn(window, "yanv")) {
    window.yanv = {};
}

window.yanv.Dimension = Dimension;
window.yanv.Variable = Variable;
window.yanv.Dataset = Dataset;