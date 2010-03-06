(set!::macro 'def::macro (fn (name args . body)
    `(set!::macro ',name (fn ,args ,@body))))

(def::macro def (name args . body)
    `(set! ',name (fn ,args ,@body)))

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

(def::macro let (vars . body)
    `((fn ,(map car vars) ,@body) ,@(map cadr vars)))

(def::macro ++ (var)
    `(set! ',var (+ ,var 1)))

(def::macro post++ (var)
    `(- (++ ,var) 1))

(def::macro assert (expr)
    `(if (not ,expr)
        (signal '(error assertion) ',expr)))

(def::macro while (test . body)
    (let ((v1 (gensym)))
      `(let ((,v1 (fn ()
        (if ,test
          (block
            ,@body
            (,v1))))))
        (,v1))))

(def::macro do-while (test . body)
    (let ((v1 (gensym)))
      `(let ((,v1 (fn ()
        ,@body
        (if ,test
            ,v1))))
        (,v1))))

(def::macro for (vardef . body)
    `(map (fn (,(car vardef)) ,@body)
        ,(cadr vardef)))
