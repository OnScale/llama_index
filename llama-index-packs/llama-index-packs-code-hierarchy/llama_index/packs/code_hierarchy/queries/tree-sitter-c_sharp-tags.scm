(class_declaration
 name: (identifier) @name.definition.class
 body: (block) @body.definition.class
 ) @definition.class

(interface_declaration
 name: (identifier) @name.definition.interface
 body: (block) @body.definition.interface
 ) @definition.interface

(method_declaration
 name: (identifier) @name.definition.method
 body: (block) @body.definition.method
 ) @definition.method

(namespace_declaration
 name: (identifier) @name.definition.module
 body: (block) @body.definition.module
) @definition.module
