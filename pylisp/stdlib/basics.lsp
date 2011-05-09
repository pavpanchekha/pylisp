;; This file is special. It is *always* run, even when still
;; setting up the interpreter. Be very careful.
;; For example, this file MAY NOT import other files in
;; any way

; Set up cxxxxxr functions
(map eval ((fn ()
  (set! 'cadr  {x: (car (cdr x))})
  
  (set! ***exp (fn (l)
                 (+ (map {x: `(,(+ "a" (car x)) (car ,(cadr x)))} l)
                    (map {x: `(,(+ "d" (car x)) (cdr ,(cadr x)))} l)
                    l)))
  (set! ***rec (fn (n)
    (if (not n)
      `((,"" x))
      (***exp (***rec (- n 1))))))

  (map {x: `(set! ,(+ "c" (car x) "r") (fn (x) ,(cadr x)))} 
       (filter {x: (!= (len (car x)) 1)} (***rec 4))))))

(set!::macro 'def::macro (fn (name args . body)
    `(set!::macro ',name (fn ,args ,@body))))
