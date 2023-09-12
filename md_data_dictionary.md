# JSON Schema

## Items

- **Items** *(object)*: Variable level metadata individual fields integrated into the variable level
metadata object within the HEAL platform metadata service.<br>  > Note, only `name` and `description` are required.
>  Listed at the end of the description are suggested "priority" levels in brackets (e.g., [<priority>]):
  1. [Required]: Needs to be filled out to be valid.
  2. [Highly recommended]: Greatly help using the data dictionary but not required. 
  3. [Optional, if applicable]: May only be applicable to certain fields.
  4. [Autopopulated, if not filled]: These fields are intended to be autopopulated from other fields but can be filled out if desired.
  5. [Experimental]: These fields are not currently used but are in development.
 Can contain additional properties.
  - **`module`** *(string)*: The section, form, survey instrument, set of measures  or other broad category used 
to group variables.


    Examples:
    ```json
    "Demographics"
    ```

    ```json
    "PROMIS"
    ```

    ```json
    "Substance use"
    ```

    ```json
    "Medical History"
    ```

    ```json
    "Sleep questions"
    ```

    ```json
    "Physical activity"
    ```

  - **`name`** *(string, required)*: The name of a variable (i.e., field) as it appears in the data. <br>    [Required]
.
  - **`title`** *(string)*: The human-readable title or label of the variable. <br>    [Highly recommended]
.

    Examples:
    ```json
    "My Variable (for name of my_variable)"
    ```

  - **`description`** *(string, required)*: An extended description of the variable. This could be the definition of a variable or the 
question text (e.g., if a survey). <br>    [Required]
.

    Examples:
    ```json
    "Definition"
    ```

    ```json
    "Question text (if a survey)"
    ```

  - **`type`** *(string)*: A classification or category of a particular data element or property expected or allowed in the dataset.<br>    -  `number` (A numeric value with optional decimal places. (e.g., 3.14))
-  `integer` (A whole number without decimal places. (e.g., 42))
-  `string` (A sequence of characters. (e.g., \"test\"))
-  `any` (Any type of data is allowed. (e.g., true))
-  `boolean` (A binary value representing true or false. (e.g., true))
-  `date` (A specific calendar date. (e.g., \"2023-05-25\"))
-  `datetime` (A specific date and time, including timezone information. (e.g., \"2023-05-25T10:30:00Z\"))
-  `time` (A specific time of day. (e.g., \"10:30:00\"))
-  `year` (A specific year. (e.g., 2023)
-  `yearmonth` (A specific year and month. (e.g., \"2023-05\"))
-  `duration` (A length of time. (e.g., \"PT1H\")
-  `geopoint` (A pair of latitude and longitude coordinates. (e.g., [51.5074, -0.1278]))
. Must be one of: `["number", "integer", "string", "any", "boolean", "date", "datetime", "time", "year", "yearmonth", "duration", "geopoint"]`.
  - **`format`**: A format taken from one of the [frictionless specification](https://specs.frictionlessdata.io/) schemas.
For example, for tabular data, there is the [Table Schema specification](https://specs.frictionlessdata.io/table-schema)<br>    Each format is dependent on the `type` specified. For example:
If `type` is "string", then see the String formats. 
If `type` is one of the date-like formats, then see Date formats.

    - **Any of**
      - : Must be one of: `["uri", "email", "binary", "uuid"]`.
      - : A format for a date variable (`date`,`time`,`datetime`).  
    \n\t* **default**: An ISO8601 format string.
    \n\t* **any**: Any parsable representation of a date/time/datetime. The implementing library can attempt to parse the datetime via a range of strategies.
    \n\t* **{PATTERN}**: The value can be parsed according to `{PATTERN}`, which `MUST` follow the date formatting syntax of C / Python [strftime](http://strftime.org/).<br>        \nExamples:<br>          `%Y-%m-%d` (for date, e.g., 2023-05-25)
  `%Y%-%d` (for date, e.g., 20230525) for date without dashes"
  `%Y-%m-%dT%H:%M:%S` (for datetime, e.g., 2023-05-25T10:30:45)
  `%Y-%m-%dT%H:%M:%SZ` (for datetime with UTC timezone, e.g., 2023-05-25T10:30:45Z)
  `%Y-%m-%dT%H:%M:%S%z` (for datetime with timezone offset, e.g., 2023-05-25T10:30:45+0300)
  `%Y-%m-%dT%H:%M` (for datetime without seconds, e.g., 2023-05-25T10:30)
  `%Y-%m-%dT%H` (for datetime without minutes and seconds, e.g., 2023-05-25T10)
  `%H:%M:%S` (for time, e.g., 10:30:45)
  `%H:%M:%SZ` (for time with UTC timezone, e.g., 10:30:45Z)
  `%H:%M:%S%z` (for time with timezone offset, e.g., 10:30:45+0300)
.
      - : The two types of formats for `geopoint` (describing a geographic point).
        - **One of**
          - *array*: A JSON array or a string parsable as a JSON array where each item is a number with the first 
as the latitude and the second as longitude. 
.
          - *object*: Contains latitude and longitude with two keys ("lat" and "long") with number items mapped to each key.

      - : The JSON object according to the geojson spec. Must be one of: `["topojson", "default"]`.
  - **`constraints`** *(object)*
    - **`maxLength`** *(integer)*: Indicates the maximum length of an iterable (e.g., array, string, or
object). For example, if 'Hello World' is the longest value of a
categorical variable, this would be a maxLength of 11.<br>      [Optional,if applicable]
.
    - **`enum`** *(array)*: Constrains possible values to a set of values.<br>      [Optional,if applicable]
.
    - **`pattern`** *(string)*: A regular expression pattern the data MUST conform to.<br>      [Optional,if applicable]
.
    - **`maximum`** *(integer)*: Specifies the maximum value of a field (e.g., maximum -- or most
recent -- date, maximum integer etc). Note, this is different then
maxLength property.<br>      [Optional,if applicable]
.
    - **`minimum`** *(integer)*: Specifies the minimum value of a field.<br>      [Optional,if applicable]
.
  - **`encodings`** *(object)*: Variable value encodings provide a way to further annotate any value within a any variable type,
making values easier to understand. <br>    
Many analytic software programs (e.g., SPSS,Stata, and SAS) use numerical encodings and some algorithms
only support numerical values. Encodings (and mappings) allow categorical values to be stored as
numerical values.<br>    Additionally, as another use case, this field provides a way to
store categoricals that are stored as  "short" labels (such as
abbreviations).<br>    [Optional,if applicable]
.

    Examples:
    ```json
    {
        "0": "No",
        "1": "Yes"
    }
    ```

    ```json
    {
        "HW": "Hello world",
        "GBW": "Good bye world",
        "HM": "Hi, Mike"
    }
    ```

  - **`ordered`** *(boolean)*: Indicates whether a categorical variable is ordered. This variable  is
relevant for variables that have an ordered relationship but not
necessarily  a numerical relationship (e.g., Strongly disagree < Disagree
< Neutral < Agree).<br>    [Optional,if applicable]
.
  - **`missingValues`** *(array)*: A list of missing values specific to a variable.<br>    [Highly recommended]
.
  - **`trueValues`** *(array)*: For boolean (true) variable (as defined in type field), this field allows
a physical string representation to be cast as true (increasing
readability of the field). It can include one or more values.<br>    [Optional, if applicable]
.
    - **Items** *(string)*

    Examples:
    ```json
    "Required"
    ```

    ```json
    "REQUIRED"
    ```

    ```json
    "required"
    ```

    ```json
    "Yes"
    ```

    ```json
    "Checked\""
    ```

  - **`falseValues`** *(array)*: For boolean (false) variable (as defined in type field), this field allows
a physical string representation to be cast as false (increasing
readability of the field) that is not a standard false value. It can include one or more values.

  - **`repo_link`** *(string)*: A link to the variable as it exists on the home repository, if applicable
.
  - **`standardsMappings`** *(array)*: A published set of standard variables such as the NIH Common Data Elements program.
[Autopopulated, if not filled].
    - **Items** *(object)*
      - **`type`** *(string)*: The **type** of mapping linked to a published set of standard variables such as the NIH Common Data Elements program.
[Autopopulated, if not filled]
.

        Examples:
        ```json
        "cde"
        ```

        ```json
        "ontology"
        ```

        ```json
        "reference_list"
        ```

      - **`label`** *(string)*: A free text **label** of a mapping indicating a mapping(s) to a published set of standard variables such as the NIH Common Data Elements program.<br>        [Autopopulated, if not filled]
.

        Examples:
        ```json
        "substance use"
        ```

        ```json
        "chemical compound"
        ```

        ```json
        "promis"
        ```

      - **`url`** *(string)*: The url that links out to the published, standardized mapping.<br>        [Autopopulated, if not filled]
.

        Examples:
        ```json
        "https://cde.nlm.nih.gov/deView?tinyId=XyuSGdTTI"
        ```

      - **`source`** *(string)*: The source of the standardized variable.


        Examples:
        ```json
        "TBD (will have controlled vocabulary)"
        ```

      - **`id`** *(string)*: The id locating the individual mapping within the given source.

  - **`relatedConcepts`** *(array)*: Mappings to a published set of concepts related to the given field such as ontological information (eg., NCI thesaurus, bioportal etc)
[Autopopulated, if not filled].
    - **Items** *(object)*
      - **`type`** *(string)*: The **type** of mapping to a published set of concepts related to the given field such as 
ontological information (eg., NCI thesaurus, bioportal etc)<br>        [Autopopulated, if not filled]
.
      - **`label`** *(string)*: A free text **label** of mapping to a published set of concepts related to the given field such as 
ontological information (eg., NCI thesaurus, bioportal etc)<br>        [Autopopulated, if not filled]
.
      - **`url`** *(string)*: The url that links out to the published, standardized concept.<br>        [Autopopulated, if not filled]
.

        Examples:
        ```json
        "https://cde.nlm.nih.gov/deView?tinyId=XyuSGdTTI"
        ```

      - **`source`** *(string)*: The source of the related concept.<br>        [Autopopulated, if not filled]
.

        Examples:
        ```json
        "TBD (will have controlled vocabulary)"
        ```

      - **`id`** *(string)*: The id locating the individual mapping within the given source.<br>        [Autopopulated, if not filled]
.
  - **`univarStats`** *(object)*: Univariate statistics inferred from the data about the given variable <br>    [Experimental]
.
    - **`median`** *(number)*
    - **`mean`** *(number)*
    - **`std`** *(number)*
    - **`min`** *(number)*
    - **`max`** *(number)*
    - **`mode`** *(number)*
    - **`count`** *(integer)*: Minimum: `0`.
    - **`twentyFifthPercentile`** *(number)*
    - **`seventyFifthPercentile`** *(number)*
    - **`categoricalMarginals`** *(array)*
      - **Items** *(object)*
        - **`name`** *(string)*
        - **`count`** *(integer)*

