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

  - **`module`**
    - **Any of**
      - *string*: The section, form, survey instrument, set of measures  or other broad category used 
to group variables.

      - : Must be one of: `[""]`.
  - **`name`** *(string, required)*: The name of a variable (i.e., field) as it appears in the data. <br>    [Required]
.
  - **`title`**
    - **Any of**
      - *string*: The human-readable title or label of the variable. <br>        [Highly recommended]
.
      - : Must be one of: `[""]`.
  - **`description`** *(string, required)*: An extended description of the variable. This could be the definition of a variable or the 
question text (e.g., if a survey). <br>    [Required]
.
  - **`type`**
    - **Any of**
      - *string*: A classification or category of a particular data element or property expected or allowed in the dataset.<br>        -  `number` (A numeric value with optional decimal places. (e.g., 3.14))
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
. Must be one of: `["integer", "geopoint", "string", "yearmonth", "number", "date", "boolean", "any", "year", "duration", "time", "datetime"]`.
      - : Must be one of: `[""]`.
  - **`format`**
    - **Any of**
      - : A format taken from one of the [frictionless specification](https://specs.frictionlessdata.io/) schemas.
For example, for tabular data, there is the [Table Schema specification](https://specs.frictionlessdata.io/table-schema)<br>        Each format is dependent on the `type` specified. For example:
If `type` is "string", then see the String formats. 
If `type` is one of the date-like formats, then see Date formats.

      - : Must be one of: `[""]`.
  - **`constraints.maxLength`**
    - **Any of**
      - *integer*: Indicates the maximum length of an iterable (e.g., array, string, or
object). For example, if 'Hello World' is the longest value of a
categorical variable, this would be a maxLength of 11.<br>        [Optional,if applicable]
.
      - : Must be one of: `[""]`.
  - **`constraints.enum`**
    - **Any of**
      - *string*: Constrains possible values to a set of values.<br>        [Optional,if applicable]
.
      - : Must be one of: `[""]`.
  - **`constraints.pattern`**
    - **Any of**
      - *string*: A regular expression pattern the data MUST conform to.<br>        [Optional,if applicable]
.
      - : Must be one of: `[""]`.
  - **`constraints.maximum`**
    - **Any of**
      - *integer*: Specifies the maximum value of a field (e.g., maximum -- or most
recent -- date, maximum integer etc). Note, this is different then
maxLength property.<br>        [Optional,if applicable]
.
      - : Must be one of: `[""]`.
  - **`constraints.minimum`**
    - **Any of**
      - *integer*: Specifies the minimum value of a field.<br>        [Optional,if applicable]
.
      - : Must be one of: `[""]`.
  - **`encodings`**
    - **Any of**
      - *string*: Variable value encodings provide a way to further annotate any value within a any variable type,
making values easier to understand. <br>        
Many analytic software programs (e.g., SPSS,Stata, and SAS) use numerical encodings and some algorithms
only support numerical values. Encodings (and mappings) allow categorical values to be stored as
numerical values.<br>        Additionally, as another use case, this field provides a way to
store categoricals that are stored as  "short" labels (such as
abbreviations).<br>        [Optional,if applicable]
.
      - : Must be one of: `[""]`.
  - **`ordered`**
    - **Any of**
      - *boolean*: Indicates whether a categorical variable is ordered. This variable  is
relevant for variables that have an ordered relationship but not
necessarily  a numerical relationship (e.g., Strongly disagree < Disagree
< Neutral < Agree).<br>        [Optional,if applicable]
.
      - : Must be one of: `[""]`.
  - **`missingValues`**
    - **Any of**
      - *string*: A list of missing values specific to a variable.<br>        [Optional, if applicable]
.
      - : Must be one of: `[""]`.
  - **`trueValues`**
    - **Any of**
      - *string*: For boolean (true) variable (as defined in type field), this field allows
a physical string representation to be cast as true (increasing
readability of the field). It can include one or more values.<br>        [Optional, if applicable]
.
      - : Must be one of: `[""]`.
  - **`falseValues`**
    - **Any of**
      - *string*: For boolean (false) variable (as defined in type field), this field allows
a physical string representation to be cast as false (increasing
readability of the field) that is not a standard false value. It can include one or more values.

      - : Must be one of: `[""]`.
  - **`repo_link`**
    - **Any of**
      - *string*: A link to the variable as it exists on the home repository, if applicable
.
      - : Must be one of: `[""]`.
  - **`standardsMappings.type`**
    - **Any of**
      - *string*: The **type** of mapping linked to a published set of standard variables such as the NIH Common Data Elements program.
[Autopopulated, if not filled]
.
      - : Must be one of: `[""]`.
  - **`standardsMappings.label`**
    - **Any of**
      - *string*: A free text **label** of a mapping indicating a mapping(s) to a published set of standard variables such as the NIH Common Data Elements program.<br>        [Autopopulated, if not filled]
.
      - : Must be one of: `[""]`.
  - **`standardsMappings.url`**
    - **Any of**
      - *string*: The url that links out to the published, standardized mapping.<br>        [Autopopulated, if not filled]
.
      - : Must be one of: `[""]`.
  - **`standardsMappings.source`**
    - **Any of**
      - *string*: The source of the standardized variable.

      - : Must be one of: `[""]`.
  - **`standardsMappings.id`**
    - **Any of**
      - *string*: The id locating the individual mapping within the given source.

      - : Must be one of: `[""]`.
  - **`relatedConcepts.type`**
    - **Any of**
      - *string*: The **type** of mapping to a published set of concepts related to the given field such as 
ontological information (eg., NCI thesaurus, bioportal etc)<br>        [Autopopulated, if not filled]
.
      - : Must be one of: `[""]`.
  - **`relatedConcepts.label`**
    - **Any of**
      - *string*: A free text **label** of mapping to a published set of concepts related to the given field such as 
ontological information (eg., NCI thesaurus, bioportal etc)<br>        [Autopopulated, if not filled]
.
      - : Must be one of: `[""]`.
  - **`relatedConcepts.url`**
    - **Any of**
      - *string*: The url that links out to the published, standardized concept.<br>        [Autopopulated, if not filled]
.
      - : Must be one of: `[""]`.
  - **`relatedConcepts.source`**
    - **Any of**
      - *string*: The source of the related concept.<br>        [Autopopulated, if not filled]
.
      - : Must be one of: `[""]`.
  - **`relatedConcepts.id`**
    - **Any of**
      - *string*: The id locating the individual mapping within the given source.<br>        [Autopopulated, if not filled]
.
      - : Must be one of: `[""]`.
  - **`univarStats.median`**
    - **Any of**
      - *number*
      - : Must be one of: `[""]`.
  - **`univarStats.mean`**
    - **Any of**
      - *number*
      - : Must be one of: `[""]`.
  - **`univarStats.std`**
    - **Any of**
      - *number*
      - : Must be one of: `[""]`.
  - **`univarStats.min`**
    - **Any of**
      - *number*
      - : Must be one of: `[""]`.
  - **`univarStats.max`**
    - **Any of**
      - *number*
      - : Must be one of: `[""]`.
  - **`univarStats.mode`**
    - **Any of**
      - *number*
      - : Must be one of: `[""]`.
  - **`univarStats.count`**
    - **Any of**
      - *integer*
      - : Must be one of: `[""]`.
  - **`univarStats.twentyFifthPercentile`**
    - **Any of**
      - *number*
      - : Must be one of: `[""]`.
  - **`univarStats.seventyFifthPercentile`**
    - **Any of**
      - *number*
      - : Must be one of: `[""]`.
  - **`univarStats.categoricalMarginals.name`**
    - **Any of**
      - *string*
      - : Must be one of: `[""]`.
  - **`univarStats.categoricalMarginals.count`**
    - **Any of**
      - *integer*
      - : Must be one of: `[""]`.

