
(def derivative (poly)
     (cdr (map {x:(* (car x) (cadr x))}
          (zip poly (range (len poly))))))

(assert (= (derivative '(7 6 6 0 0 0 1))
           '(6 12 0 0 0 6)))


(def poly-eval (poly x)
     (if (not poly)
       0
       (+ (car poly) (* x (poly-eval (cdr poly) x)))))

(assert (= (poly-eval '(1 2 3 4 1) .5)
           3.3125))


(def newton-improve (guess poly)
     (- guess (/ (poly-eval poly guess)
                 (poly-eval (derivative poly) guess))))


(def solve (poly)
     (let ((old 34) (curr 17) (epsilon (^ .1 8)))
         (while (> (abs (- curr old)) epsilon)
                (set! 'old curr)
                (set! 'curr (newton-improve curr poly)))

         curr))

(assert (= (solve `(1 ,(- 1) 0 1)) (- 0 1.324717957244746)))

