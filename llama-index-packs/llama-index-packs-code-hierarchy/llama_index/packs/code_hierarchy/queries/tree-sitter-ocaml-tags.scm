; Modules
;--------

(
  (comment)? @doc .
  (module_definition (module_binding (module_name) @name.definition.module) @definition.module)
  (#strip! @doc "^\\(\\*\\*?\\s*|\\s\\*\\)$")
)

; Modules types
;--------------

(
  (comment)? @doc .
  (module_type_definition (module_type_name) @name.definition.interface) @definition.interface
  (#strip! @doc "^\\(\\*\\*?\\s*|\\s\\*\\)$")
)

; Functions
;----------

(
  (comment)? @doc .
  (value_definition
    [
      (let_binding
        pattern: (value_name) @name.definition.function
        (parameter))
      (let_binding
        pattern: (value_name) @name.definition.function
        body: [(fun_expression) (function_expression)])
    ] @definition.function
  )
  (#strip! @doc "^\\(\\*\\*?\\s*|\\s\\*\\)$")
)

(
  (comment)? @doc .
  (external (value_name) @name.definition.function) @definition.function
  (#strip! @doc "^\\(\\*\\*?\\s*|\\s\\*\\)$")
)

; Operator
;---------

(
  (comment)? @doc .
  (value_definition
    (let_binding
      pattern: (parenthesized_operator [
        (prefix_operator)
        (infix_operator)
        (hash_operator)
        (indexing_operator)
        (let_operator)
        (and_operator)
        (match_operator)
      ] @name.definition.function)) @definition.function)
  (#strip! @doc "^\\(\\*\\*?\\s*|\\s\\*\\)$")
)

; Classes
;--------

(
  (comment)? @doc .
  [
    (class_definition (class_binding (class_name) @name.definition.class) @definition.class)
    (class_type_definition (class_type_binding (class_type_name) @name.definition.class) @definition.class)
  ]
  (#strip! @doc "^\\(\\*\\*?\\s*|\\s\\*\\)$")
)

; Methods
;--------

(
  (comment)? @doc .
  (method_definition (method_name) @name.definition.method) @definition.method
  (#strip! @doc "^\\(\\*\\*?\\s*|\\s\\*\\)$")
)
