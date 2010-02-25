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
     (handle 'test (fn ()
         (set! flag True)
         (control ignore)))
     (signal 'test))
(fail?)
(assert flag)

; macros
(def::macro betrue (a b)
    True)
(assert (betrue 1 17))

; while loops
(set! a 1)
(while (< a 1000)
    (set! a (* a 2)))
(assert (= a 1024))

; Cool! We won!
(print 'Success)
