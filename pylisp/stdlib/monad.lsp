; First, a few helpers

(def compose (f g)
     {. args: (f (g . args))})

(def concat (l)
     (+ . l))

(set! 'concatMap (compose concat map))

; Summary of Monad class syntax:
; (Monad a) -> a monad
; it's callable:
; ((Monad a) f g h i) ->
;   (((((Monad a).bind f).bind g).bind h).bind i)
; Except that the above is still invalid syntax (it has to be uglier)
; Lastly, one can pierce a monad with the pierce member function.

(class Monad ()
  (def::method __init__ (f)
    (signal '(error not-implemented) "Monad.__init__ intended for subclassing"))

  (def::method pierce (f)
    (signal '(error not-implemented) "Monad.pierce intended for subclassing"))

  (def::method bind (f)
    (signal '(error not-implemented) "Monad.bind intended for subclassing"))

  (def::method __call__ (. funcs)
    (if (not funcs)
      self
      ((self.bind (car funcs)) . (cdr funcs)))))

; ListMonad
; bind must map the function across the internal list

(class ListMonad (Monad)
  (def::method __init__ (args)
    (set! self.l args))

  (def::method bind (f)
    (ListMonad (map f self.l)))
  
  (def::method pierce (f)
    self.l))

; Tests for ListMonad
(assert (= ((:: ((ListMonad (range 10)) {x: (* x 2)}) 'pierce)) '(0 2 4 6 8 10 12 14 16 18)))

; StateMonad
(class state-set ()
  (def::method __init__ (val)
    (set! self.val val)))

(class StateMonad (Monad)
  (def::method __init__ (val)
    (set! self.v val))

  (def::method bind (f)
    (let (ret (f self.v))
      (if (is ret state-set)
        (StateMonad ret.val)
        self)))

  (def::method pierce (f)
    self.v))

((StateMonad 5) {v:(assert (= v 5))} {v:(state-set 6)} {v:(assert (= v 6))})

; do syntax
; (do MONAD var
;   expr1
;   expr2
;   expr3)
(use listtools)

(def::macro do (m var . exprs)
  `(,m ,@(for (expr exprs) `{,var:,expr})))

(do (StateMonad 5) v
  (assert (= v 5))
  (state-set 6)
  (assert (= v 6)))
