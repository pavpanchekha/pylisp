(def::reader #& (body)
  (fn (~) (eval body)))

(def::reader #<< (body)
  (print (eval body)))
