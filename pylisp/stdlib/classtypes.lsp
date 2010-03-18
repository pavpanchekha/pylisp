
(def::macro class (name bases . body)
    `(set! ',name (#class ,bases ,@body)))

(def::macro class::simple (name fields)
    (let ((qfields (map {x:`',x} fields)))
        `(class ,name ()
             (def::method __init__ ,fields
                  ,@(for (qfield qfields)
                         `(set! (:: self ,qfield) ,qfield))))))
