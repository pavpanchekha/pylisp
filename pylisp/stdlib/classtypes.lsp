
(def::macro class (name bases . body)
  `(set! ',name (#class ,bases ,@body)))

(def::macro class::simple (name fields)
  `(class ,name ()
     (def::method __init__ ,fields
       ,@(for (field fields)
           `(set! (:: self ',field) ,field)))))

(def::macro singleton (name)
  `(block (class ,name ()
            (def::method __str__ () ',name))
          (set! ',name (,name))))

