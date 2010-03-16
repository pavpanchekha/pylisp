;; This file is special. It is *always* run, even when still
;; setting up the interpreter. Be vary careful.
;; For example, this file MAY NOT import other files in
;; any way

(set! 'cadr  (fn (x) (car (cdr x))))
(set! 'cddr  (fn (x) (cdr (cdr x))))

