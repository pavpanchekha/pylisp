; Finds sqrt(1 + 2sqrt(1 + 3sqrt(1 + 4sqrt(...))))

(use math)

(def n-iter (n m)
     (if (not n)
         1
         (math.sqrt (+ 1 (* (+ m 1) (n-iter (- n 1) (+ m 1)))))))

(print (n-iter 50 1))
