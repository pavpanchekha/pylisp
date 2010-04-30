(def::macro def (name args . body)
  `(set! ',name (fn ,args ,@body)))

(def::macro def::class (name args . body)
  `(set! ',name (class-method (fn ,(cons 'cls args) ,@body))))

(def::macro def::static (name args . body)
  `(set! ',name (static-method (fn ,(cons 'cls args) ,@body))))

; Look ma! No explicit self!
(def::macro def::method (name args . body)
  `(def ,name ,(cons 'self args) ,@body))

(def::macro def::abstract (name)
  `(def ,name () (signal '(error not-implemented) ,(+ name " intended for subclassing"))))

(def::macro def::reader (name args . body)
  `(block
     (set! (:: (def ,name (#intp ,@args) ,@body) '_fexpr) #t)
     (set!::reader ',name)))
