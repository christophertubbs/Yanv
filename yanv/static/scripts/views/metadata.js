
import {DataResponse} from "../responses.js";
import {Dataset} from "../model.js";
import {createFieldSet, createSimpleList, createTable} from "../elements.js";

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
     * @param tabSelector {string}
     */
    addTab = (tabSelector) => {
        const tabs = $(tabSelector);

        if ($(`${tabSelector} li#${this.data_id}-tab`).length === 0) {
            /**
             * @type {HTMLLIElement}
             */
            const tab = document.createElement("li")

            /**
             *
             * @type {HTMLAnchorElement}
             */
            const tabLink = document.createElement("a")
            tabLink.href = `#${this.data_id}`;
            tabLink.innerText = this.data_id;

            tab.appendChild(tabLink);
            tabs.append(tab);
        }
    }

    /**
     *
     * @param rootSelector {string}
     * @param tabSelector {string}
     */
    render = (rootSelector, tabSelector) => {
        /**
         *
         * @type {jQuery}
         */
        const root = $(rootSelector);

        if (!root) {
            throw new Error(`No elements could be found at '${rootSelector}' - a new view cannot be rendered`)
        }

        if ($(tabSelector).length === 0) {
            throw new Error(`No tab list could be found at '${tabSelector}' - a new view cannot be rendered`)
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

        let globalAttributes = this.#renderAttributesTable(
            this.dataset.attributes,
            true,
            null
        )

        globalAttributes = createTable(
            `${this.data_id}-global-attributes`,
            "Global Attributes",
            this.dataset.attributes
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

        this.addTab(tabSelector);
        root.tabs("refresh");

        const newTabIndex = $(tabSelector).length - 1;
        root.tabs("option", "active", newTabIndex);
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
        dimensionsFieldset.className = "yanv-dimensions-fields yanv-fields";
        dimensionsFieldset.name = "Dimensions";

        const legend = document.createElement("legend");
        legend.className = "yanv-legend"
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

        const minimumCell = document.createElement("th");
        minimumCell.textContent = "Minimum Value";
        minimumCell.attributes['data-column'] = "minimum";

        const maximumCell = document.createElement("th");
        maximumCell.textContent = "Maximum Value";
        maximumCell.attributes['data-column'] = "maximum";

        const countHeaderCell = document.createElement("th");
        countHeaderCell.textContent = "Count";
        countHeaderCell.attributes['data-column'] = 'count';

        header.appendChild(nameHeaderCell);
        header.appendChild(typeHeaderCell);
        header.appendChild(minimumCell);
        header.appendChild(maximumCell);
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
            row.attributes['data-minimum'] = dimension.minimum;
            row.attributes['data-maximum'] = dimension.maximum;
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

            let minimumCell = document.createElement("td");
            minimumCell.id = `${dimensionsID}-${dimension.name}-minimum`;
            minimumCell.innerText = dimension.minimum;
            minimumCell.attributes['data-column'] = 'minimum';

            row.appendChild(minimumCell)

            let maximumCell = document.createElement("td")
            maximumCell.id = `${dimensionsID}-${dimension.name}-maximum`
            maximumCell.innerText = dimension.maximum;
            maximumCell.attributes['data-column'] = 'maximum';

            row.appendChild(maximumCell);

            let countCell = document.createElement("td");
            countCell.id = `${dimensionsID}-${dimension.name}-count`
            countCell.innerText = dimension.count;
            countCell.attributes['data-column'] = 'count';

            row.appendChild(countCell);

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

            let datatype;

            if (/^\|S1/.test(variable.datatype)) {
                datatype = '';
            }
            else if (/^\|S\d+/.test(variable.datatype)) {
                datatype = "string ";
            }
            else {
                datatype = `${variable.datatype} `;
            }

            let variableName = `${datatype}${variable.name}`;

            if (variable.dimensions.length > 0) {
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
            plotButton.className = [
                'yanv-button',
                'yanv-plot-button'
            ].join(" ");

            toolbar.appendChild(plotButton);

            variableContents.appendChild(toolbar);

            variableContents.appendChild(
                this.#renderAttributesTable(variable.attributes, notGlobal, variableID)
            );

            if (variable.examples.length > 0) {
                /**
                 * @type {HTMLFieldSetElement}
                 */
                const exampleContainer = createFieldSet(
                    `${variableID}-examples`,
                    "Example Values",
                    "Example Values"
                );
                let exampleList = createSimpleList(
                    `${variableID}-example-list`,
                    "Examples",
                    variable.examples
                );

                exampleContainer.appendChild(exampleList)
                variableContents.appendChild(exampleContainer);
            }

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

