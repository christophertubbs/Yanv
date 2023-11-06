
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

    render = (rootSelector) => {

    }

    /**
     *
     * @param dimensions {Dimension[]}
     */
    renderDimensions = (dimensions) => {
        const dimensionsID = `${this.data_id}-dimensions`;

        /**
         * @type {HTMLFieldSetElement}
         */
        const dimensionsFieldset = document.createElement("fieldset")
        dimensionsFieldset.id = dimensionsID;
        dimensionsFieldset.className = "dimensions-fields";
        dimensionsFieldset.name = "Dimensions";

        const legend = document.createElement("legend");
        legend.textContent = "Dimensions";

        dimensionsFieldset.appendChild(legend);

        /**
         * @type {HTMLTableElement}
         */
        const dimensionsTable = document.createElement("table")
        dimensionsTable.className = "dimensions-table"
        dimensionsTable.id = `${dimensionsID}-table`;

        let columns = [];
        let isFirstDimension = true;
        for (let dimension of dimensions) {
            /**
             * @type {string[]}
             */
            let thisDimensionsColumns = Object.keys(dimension.attributes);

            if (isFirstDimension) {
                columns += thisDimensionsColumns;
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
                columns = newBeginning + columns.splice(1);
            }
        }

        /**
         * @type {HTMLTableRowElement}
         */
        const header = document.createElement("tr")
        header.id = `${dimensionsID}-header`;
        header.className = "header-row dimensions-header"

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
                rowID % 2 === 0 ? "odd" : "even",
                "dimensions-row"
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
     */
    renderVariables = (variables) => {
        /**
         *
         * @type {HTMLDivElement}
         */
        const accordion = document.create("div");
        accordion.id = `${this.data_id}-accordion`;
        accordion.className = "variable-accordion"

        for (let variable of variables) {
            const variableID = `${this.data_id}-${variable.name}`;

            /**
             *
             * @type {HTMLHeadingElement}
             */
            let variableHeader = document.createElement("h3")
            variableHeader.id = `${variableID}-bar`;
            variableHeader.className = "variable-bar";

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


            let attributesTable = document.createElement("table");
            attributesTable.id = `${variableID}-attributes`;
            attributesTable.className = `${variableID} variable-attributes`;

            let rowID = 0;

            for (let [key, value] of Object.entries(variable.attributes)) {
                let attributeID = `${variableID}-${key}`;

                /**
                 *
                 * @type {HTMLTableRowElement}
                 */
                let row = document.createElement("tr")
                let cssClasses = [
                    `${rowID % 2 === 0 ? "even" : "odd"}-row`,
                    "variable-attribute"
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
                keyCell.className = "attribute-name";
                keyCell.id = `${attributeID}-key`;
                keyCell.textContent = key;

                row.appendChild(keyCell);

                /**
                 * @type {HTMLTableCellElement}
                 */
                let valueCell = document.createElement("td");
                valueCell.className = "attribute-value";
                valueCell.id = `${attributeID}-value`
                valueCell.textContent = value;

                row.appendChild(valueCell);

                attributesTable.appendChild(row);
                rowID++;
            }

            variableContents.appendChild(attributesTable);
            accordion.appendChild(variableContents);
        }

        return accordion;
    }

    /**
     *
     * @param attributes {{string: any}}
     */
    renderAttributes = (attributes) => {

    }
}

