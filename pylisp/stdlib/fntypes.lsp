(def::macro def (name args . body)
    `(set! ',name (fn ,args ,@body)))

(def::macro def::class (name args . body)
    `(set! ',name (class-method
                    (fn ,(cons 'cls args) ,@body))))

(def::macro def::static (name args . body)
    `(set! ',name (static-method
                    (fn ,(cons 'cls args) ,@body))))

; Look ma! No explicit self!
(def::macro def::method (name args . body)
    `(def ,name ,(cons 'self args) ,@body))

