
import {DataResponse} from "../responses.js";
import {Dataset} from "../model.js";

export class DatasetView {
    /**
     * @member {DataResponse}
     */
    data

    /**
     * @member {Dataset}
     */
    dataset
    /**
     * @member {string}
     */
    data_id

    /**
     *
     * @param data {DataResponse}
     */
    constructor (data) {
        this.data = data;
        this.data_id = data.data_id;
        this.dataset = new Dataset(data.data);
    }

    /**
     *
     * @param rootSelector {string}
     */
    render = (rootSelector) => {
        /**
         *
         * @type {jQuery}
         */
        const root = $(rootSelector);

        if (!root) {
            throw new Error(`No elements could be found at '${rootSelector}'`)
        }

        /**
         *
         * @type {HTMLDivElement}
         */
        const container = document.createElement("div");
        container.id = this.data_id;

        const containerCSSClasses = [
            `yanv-container`,
            `yanv-dataset`
        ]

        container.className = containerCSSClasses.join(" ");
        container.attributes['data-dataset'] = this.data_id;

        const renderedDimensions = this.renderDimensions(this.dataset.dimensions);

        if (renderedDimensions) {
            container.appendChild(renderedDimensions);
        }

        const renderedVariables = this.renderVariables(this.dataset.variables);

        if (renderedVariables) {
            container.appendChild(renderedVariables);
        }

        const globalAttributes = this.#renderAttributesTable(
            this.dataset.attributes,
            true,
            null
        )

        if (globalAttributes) {
            const globalAttributesField = document.createElement("fieldset");
            globalAttributesField.id = `${this.data_id}-global-fields`;
            const cssClasses = [
                "yanv-global-attributes-fieldset"
            ];
            globalAttributesField.className = cssClasses.join(" ");

            const globalAttributeLegend = document.createElement("legend")
            globalAttributeLegend.id = `${this.data_id}-global-attributes-legend`
            const legendCSSClasses = [
                'yanv-legend',
                'yanv-global-attributes-legend'
            ]
            globalAttributeLegend.className = legendCSSClasses.join(" ");
            globalAttributeLegend.innerText = "Global Attributes"
            globalAttributesField.appendChild(globalAttributeLegend);
            globalAttributesField.appendChild(globalAttributes);
            container.appendChild(globalAttributesField);
        }

        root.append(container)

        $(".yanv-accordion").accordion();
    }

    /**
     *
     * @param dimensions {Dimension[]}
     * @returns {HTMLFieldSetElement}
     */
    renderDimensions = (dimensions) => {
        const dimensionsID = `${this.data_id}-dimensions`;

        /**
         * @type {HTMLFieldSetElement}
         */
        const dimensionsFieldset = document.createElement("fieldset")
        dimensionsFieldset.id = dimensionsID;
        dimensionsFieldset.className = "yanv-dimensions-fields";
        dimensionsFieldset.name = "Dimensions";

        const legend = document.createElement("legend");
        legend.textContent = "Dimensions";

        dimensionsFieldset.appendChild(legend);

        /**
         * @type {HTMLTableElement}
         */
        const dimensionsTable = document.createElement("table")
        dimensionsTable.className = "yanv-dimensions-table"
        dimensionsTable.id = `${dimensionsID}-table`;

        let columns = [];
        let isFirstDimension = true;
        for (let dimension of dimensions) {
            /**
             * @type {string[]}
             */
            let thisDimensionsColumns = Object.keys(dimension.attributes);

            if (isFirstDimension) {
                columns = thisDimensionsColumns;
                isFirstDimension = false;
                continue;
            }

            let columnsToRemove = [];
            for (let column of columns) {
                if (!thisDimensionsColumns.includes(column)) {
                    columnsToRemove.push(column);
                }
            }

            for (let column of columnsToRemove) {
                let columnIndex = columns.indexOf(column);
                let newBeginning = columns.splice(0, columnIndex);
                columns = newBeginning.concat(columns.splice(1));
            }
        }

        /**
         * @type {HTMLTableRowElement}
         */
        const header = document.createElement("tr")
        header.id = `${dimensionsID}-header`;
        header.className = "yanv-header-row yanv-dimensions-header"

        const nameHeaderCell = document.createElement("th");
        nameHeaderCell.textContent = "Name";
        nameHeaderCell.attributes['data-column'] = 'name';

        const typeHeaderCell = document.createElement("th");
        typeHeaderCell.textContent = "Data Type";
        typeHeaderCell.attributes['data-column'] = 'datatype';

        const countHeaderCell = document.createElement("th");
        countHeaderCell.textContent = "Count";
        countHeaderCell.attributes['data-column'] = 'count';

        header.appendChild(nameHeaderCell);
        header.appendChild(typeHeaderCell);
        header.appendChild(countHeaderCell);

        for (let column of columns) {
            let headerCell = document.createElement("th");
            headerCell.textContent = column;
            headerCell.attributes['data-column'] = column;

            header.appendChild(headerCell);
        }

        dimensionsTable.appendChild(header);

        let rowID = 0;
        for (let dimension of dimensions) {
            let row = document.createElement("tr")
            row.id = `${dimensionsID}-${dimension.name}`;
            let classList = [
                `yanv-${rowID % 2 === 0 ? "odd" : "even"}-row`,
                'yanv-row',
                "yanv-dimension"
            ]
            row.className = classList.join(" ");

            row.attributes['data-dimension'] = rowID;
            row.attributes['data-name'] = dimension.name;
            row.attributes['data-datatype'] = dimension.datatype;
            row.attributes['data-count'] = dimension.count;

            let nameCell = document.createElement("td")
            nameCell.id = `${dimensionsID}-${dimension.name}-name`;
            nameCell.innerText = dimension.name;
            nameCell.attributes['data-column'] = 'name';

            row.appendChild(nameCell);

            let typeCell = document.createElement("td")
            typeCell.id = `${dimensionsID}-${dimension.name}-data-type`;
            typeCell.innerText = dimension.datatype;
            typeCell.attributes['data-column'] = "datatype";

            row.appendChild(typeCell);

            let countCell = document.createElement("td");
            countCell.id = `${dimensionsID}-${dimension.name}-count`
            countCell.innerText = dimension.count;
            countCell.attributes['data-column'] = 'count';

            for (let column of columns) {
                let cell = document.createElement("td")
                cell.id = `${dimensionsID}-${dimension.name}-${column}`;
                cell.innerText = dimension.attributes[column];
                cell.attributes['data-column'] = column;

                row.attributes[`data-${column}`] = dimension.attributes[column];
                row.appendChild(cell);
            }

            dimensionsTable.appendChild(row);

            rowID++;
        }

        dimensionsFieldset.appendChild(dimensionsTable);


        return dimensionsFieldset;
    }

    /**
     *
     * @param variables {Variable[]}
     * @returns {HTMLDivElement}
     */
    renderVariables = (variables) => {
        /**
         *
         * @type {HTMLDivElement}
         */
        const accordion = document.createElement("div");
        accordion.id = `${this.data_id}-accordion`;
        accordion.className = "yanv-variable-accordion yanv-accordion"

        const notGlobal = false;

        for (let variable of variables) {
            const variableID = `${this.data_id}-${variable.name}`;

            /**
             *
             * @type {HTMLHeadingElement}
             */
            let variableHeader = document.createElement("h3")
            variableHeader.id = `${variableID}-bar`;
            variableHeader.className = "yanv-variable-bar";

            let variableName = `${variable.datatype} ${variable.name}`;

            if (variable.dimensions) {
                let dimensionNames = [];
                for (let dimension of variable.dimensions) {
                    dimensionNames.push(dimension.name)
                }
                variableName = `${variableName}(${dimensionNames.join(", ")})`
            }

            variableHeader.textContent = variableName;
            accordion.appendChild(variableHeader);

            /**
             *
             * @type {HTMLDivElement}
             */
            let variableContents = document.createElement("div");
            variableContents.id = `${variableID}-contents`;

            const toolbar = document.createElement("div");
            toolbar.id = `${variableID}-toolbar`;
            const toolbarClassNames = [
                "yanv-toolbar",
                "yanv-variable-toolbar"
            ];

            toolbar.className = toolbarClassNames.join(" ");

            /**
             *
             * @type {HTMLButtonElement}
             */
            let plotButton = document.createElement("button")
            plotButton.id = `plot-${variableID}`
            plotButton.innerText = "Plot";

            toolbar.appendChild(plotButton);

            variableContents.appendChild(toolbar);

            variableContents.appendChild(
                this.#renderAttributesTable(variable.attributes, notGlobal, variableID)
            );
            accordion.appendChild(variableContents);
        }

        return accordion;
    }

    /**
     *
     * @param attributes {{string: any}}
     * @param isGlobal {boolean}
     * @param variableID {string|undefined|null}
     * @returns {HTMLTableElement|HTMLParagraphElement}
     */
    #renderAttributesTable = (attributes, isGlobal, variableID) => {
        if (isGlobal === null || isGlobal === undefined) {
            isGlobal = false;
        }

        const scope = isGlobal ? "global" : "variable";

        if (!variableID && !isGlobal) {
            throw new Error(
                "An attributes table cannot be rendered - a table is marked as variable level yet has not variable ID"
            );
        }
        else if (!variableID) {
            variableID = "global";
        }

        const variableName = isGlobal ? null : variableID.replace(`${this.data_id}-`, "")

        if (attributes === null || attributes === undefined || Object.keys(attributes).length === 0) {
            /**
             *
             * @type {HTMLParagraphElement}
             */
            const lackOfAttributesParagraph = document.createElement("p");

            if (isGlobal) {
                lackOfAttributesParagraph.innerText = `Dataset ${this.data_id} has no global attributes`;
            }
            else {
                lackOfAttributesParagraph.innerText = `The ${variableName} variable has no attributes`;
            }

            return lackOfAttributesParagraph;
        }

        let attributesTable = document.createElement("table");
        attributesTable.id = `${variableID}-attributes`;

        const tableCSSClasses = [
            `yanv-table`,
            "yanv-attributes",
            `yanv-${scope}-attributes`
        ];

        attributesTable.className = tableCSSClasses.join(" ");

        let rowID = 0;

        for (let [key, value] of Object.entries(attributes)) {
            let attributeID = `${variableID}-${key}`;

            /**
             *
             * @type {HTMLTableRowElement}
             */
            let row = document.createElement("tr")
            let cssClasses = [
                `yanv-${rowID % 2 === 0 ? "even" : "odd"}-row`,
                'yanv-row',
                'yanv-attribute',
                `yanv-${scope}-attribute`
            ];

            row.className = cssClasses.join(" ");
            row.id = attributeID;

            row.attributes['data-key'] = key;
            row.attributes['data-value'] = value;
            row.attributes['data-row'] = rowID;

            /**
             * @type {HTMLTableCellElement}
             */
            let keyCell = document.createElement("td");
            keyCell.className = `yanv-attribute-name yanv-${scope}-attribute-name`;
            keyCell.id = `${attributeID}-key`;
            keyCell.textContent = key;

            row.appendChild(keyCell);

            /**
             * @type {HTMLTableCellElement}
             */
            let valueCell = document.createElement("td");
            valueCell.className = `yanv-attribute-value yanv-${scope}-attribute-value`;
            valueCell.id = `${attributeID}-value`
            valueCell.textContent = value;
            valueCell.attributes['data-attribute'] = key;

            row.appendChild(valueCell);

            attributesTable.appendChild(row);
            rowID++;
        }

        return attributesTable;
    }
}

