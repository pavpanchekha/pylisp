; math
(assert (= (mod (^ 2010 17) 17) (mod 2010 17)))

; let
(let ((a 1))
  (assert (= a 1)))

; set!
(set! a 10)
(assert (= a 10))

; fn
(assert (= ((fn (x) (* x x)) 10) 100))

; def & recursion
(def reverse (l) (reverse-aux l '()))
(def reverse-aux (l acc)
    (if (not l)
      acc
      (reverse-aux
        (cdr l)
        (cons (car l) acc))))
(assert (= (reverse '(1 2 3)) '(3 2 1)))

; exceptions
(set! flag False)
(def fail? ()
     (catch 'test (fn () (set! flag True)))
     (throw (error 'test)))
(fail?)
(assert flag)



; Cool! We won!
(print 'Success)
