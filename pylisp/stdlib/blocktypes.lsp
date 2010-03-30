
(def::macro let (vars . body)
    `((fn ,(map car vars) ,@body) ,@(map cadr vars)))

(def while* (test-fn body-fn)
  (if (test-fn)
    (block (body-fn) (while* test-fn body-fn))))

(def::macro while (test . body)
  `(while* {:,test} {:,@body}))

(def::macro do-while (test . body)
  `(block
     ,@body
     (while ,test ,@body)))

(def::macro for (vardef . body)
    `(map (fn (,(car vardef)) ,@body)
        ,(cadr vardef)))

(def::macro map::macro (f l)
    `(block ,@(map (fn (x) (list f x)) l)))

