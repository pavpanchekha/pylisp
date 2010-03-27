
(def::macro let (vars . body)
    `((fn ,(map car vars) ,@body) ,@(map cadr vars)))

(def::macro while (test . body)
    (let ((v1 (gensym)))
      `(let ((,v1 {:
        (if ,test
          (block
            ,@body
            (,v1)))}))
        (,v1))))

(def::macro do-while (test . body)
    (let ((v1 (gensym)))
      `(let ((,v1 {:
        ,@body
        (if ,test
            (,v1))}))
        (,v1))))

(def::macro for (vardef . body)
    `(map (fn (,(car vardef)) ,@body)
        ,(cadr vardef)))

(def::macro map::macro (f l)
    `(block ,@(map (fn (x) (list f x)) l)))

