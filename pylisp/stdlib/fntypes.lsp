(def::macro def (name args . body)
  `(set! ',name (fn ,args ,@body)))

(def::macro def::class (name args . body)
  `(set! ',name (class-method (fn ,(cons 'cls args) ,@body))))

(def::macro def::static (name args . body)
  `(set! ',name (static-method (fn ,args ,@body))))

; Look ma! No explicit self!
(def::macro def::method (name args . body)
  `(def ,name ,(cons 'self args) ,@body))

(def::macro def::abstract (name)
  `(def ,name () (signal '(error not-implemented) ,(+ name " intended for subclassing"))))

(def::macro def::reader (name args . body)
  (let (g1 (gensym))
    `(let (,g1 (fn ,(+ '(#intp) args) ,@body))
       (set! (:: ,g1 '_fexpr) #t)
       (set!::reader ',name ,g1))))
