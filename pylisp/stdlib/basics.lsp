;; This file is special. It is *always* run, even when still
;; setting up the interpreter. Be very careful.
;; For example, this file MAY NOT import other files in
;; any way

(set! 'cadr  {x: (car (cdr x))})
(set! 'cddr  {x: (cdr (cdr x))})

(set!::macro 'def::macro (fn (name args . body)
    `(set!::macro ',name (fn ,args ,@body))))
