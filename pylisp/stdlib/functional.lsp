
(def I (x) x)

(def K (x)
     (fn (y) x))

(def S (n)
     (fn (f)
         (fn (x)
             (f ((n f) x)))))
