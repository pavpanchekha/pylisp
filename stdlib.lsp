(def I (x) x)
(def K (x)
     (fn (y) x))

(def map (f l)
  (if (not l)
     nil
     (cons
       (f (car l))
       (map f (cdr l)))))

(def::macro and (x y)
  `(if ,x ,y ,x))

(def::macro or (x y)
  `(if ,x ,x ,y))

(def or (x y)
  (if x y x))

(def and (x y)
  (if x x y))

(def xor (x y)
     (or (and x (not y)) (and y (not x))))

(def cadr (x) (car (cdr x)))
(def cddr (x) (cdr (cdr x)))

(def::macro let (vars body)
    `((fn ,(map car vars) ,body) ,@(map cadr vars)))

(def::macro assert (expr)
    `(if (not ,expr)
        (throw (error 'assertion ',expr))))

(def::macro while (test body)
    (let ((v1 (gensym)))
      `(let ((,v1 (fn ()
        (if ,test
          (block
            ,body
            (,v1))))))
        (,v1))))
