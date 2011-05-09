
; The macro `lazy` returns a thunk which can be
; called arbitrarily many times; the expression
; is evaluated only once.
(def::macro lazy (expr)
  (let (v1 (gensym))
    `({:
        (def ,v1 ()
          (if (has ,v1 'value)
            (:: ,v1 'value)
            (set! (:: ,v1 'value) ,expr)))})))

