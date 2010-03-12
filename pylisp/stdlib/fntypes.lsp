(def::macro def::class (name args . body)
    `(set! ',name (class-method
                    (fn ,(cons 'cls args) ,@body))))

(def::macro def::static (name args . body)
    `(set! ',name (static-method
                    (fn ,(cons 'cls args) ,@body))))

(def::macro def::method (name args . body)
    `(def ,name ,(cons 'self args) ,@body))

