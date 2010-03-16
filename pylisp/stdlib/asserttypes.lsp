(def assert::= (. exprs) exprs)
(set! 'assert::!= assert::=)
(set! 'assert::> assert::=)
(set! 'assert::< assert::=)
(set! 'assert::<= assert::=)
(set! 'assert::>= assert::=)

(def::macro assert (expr)
    `(if (not ,expr)
       (signal '(error assertion) ',expr)))

(assert #t)
(assert (= 3 3))
