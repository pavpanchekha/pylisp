(import math)

(set! '*epsilon* (^ .1 10))

(def exp (z)
     (Complex.polar (math.exp z.real) z.imag))

(def arg (z)
     (math.atan2 z.imag z.real))

(def log (z)
     (Complex (math.log (abs z)) (arg z)))
       

(class Complex ()
       (def::method __init__ (re im)
            (set! self.real re)
            (set! self.imag im))

       (def::class polar (norm arg)
             (cls (* norm (math.cos arg))
                  (* norm (math.sin arg))))

       (def::method __add__ (other)
            (Complex (+ self.real other.real)
                     (+ self.imag other.imag)))

       (def::method __sub__ (other)
            (Complex (- self.real other.real)
                     (- self.imag other.imag)))

       (def::method __mul__ (other)
            (Complex (- (* self.real other.real)
                        (* self.imag other.imag))
                     (+ (* self.real other.imag)
                        (* self.imag other.real))))

       (def::method __abs__ ()
            (math.sqrt (+ (^ self.real 2) (^ self.imag 2))))

       (def::method _reciprocal ()
            (let ((normsq (^ (abs self) 2)))
              (Complex (/ self.real normsq)
                       (/ (- self.imag) normsq))))

       (def::method __div__ (other)
            (* (other._reciprocal) self))
       
       (def::method __eq__ (other)
            (< (abs (- self other)) *epsilon*))
       
       (def::method __ne__ (other)
            (not (= self other)))
       
       (def::method __invert__ (other)
            (Complex self.real (- self.imag)))
       
       (def::method __str__ ()
            (+ (str self.real)
               (if (< self.imag 0) " - " " + ")
               (str (abs self.imag))))

       (def::method __pow__ (other)
            (exp (* other (log self)))))

(set! 'z (Complex 1 1))
(set! 'w (Complex 2 (- 3)))

(assert (= (+ z w) (Complex 3 (- 2))))
(assert (= (- z w) (Complex (- 1) 4)))
(assert (= (* z w) (Complex 5 (- 1))))
(assert (= (/ w z) (Complex (- .5) (- 2.5))))
(assert (= (conj w) (Complex 2 3)))
(assert (= (Complex.polar 1 1)
           (Complex .54030230587 .84147098481)))
(assert (= (exp (Complex 3 (- 1)))
           (Complex 10.85226191419796
                    (- 16.9013965351501))))
(assert (= (^ z w) (Complex 18.19499465428708
                            10.68706149930325)))

