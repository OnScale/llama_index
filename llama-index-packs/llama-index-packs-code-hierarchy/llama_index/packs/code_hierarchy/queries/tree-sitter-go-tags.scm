(
  (comment)* @doc
  .
  (function_declaration
    name: (identifier) @name.definition.function
    body: (block) @body.definition.function) @definition.function
  (#strip! @doc "^//\\s*")
  (#set-adjacent! @doc @definition.function)
)

(
  (comment)* @doc
  .
  (method_declaration
    name: (field_identifier) @name.definition.method
    body: (block) @body.definition.method) @definition.method
  (#strip! @doc "^//\\s*")
  (#set-adjacent! @doc @definition.method)
)

(type_spec
  name: (type_identifier) @name.definition.type
  body: (block) @body.definition.type) @definition.type
