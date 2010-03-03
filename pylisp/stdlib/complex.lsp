(import math)

(set! '*epsilon* (^ .1 10))

(def exp (z)
     (Complex.polar (math.exp z.real) z.imag))

(def arg (z)
     (math.atan2 z.imag z.real))

(def log (z)
     (Complex (math.log (abs z)) (me.arg z)))
       

(class Complex ()
       (def __init__ (self re im)
            (set! self.real re)
            (set! self.imag im))

       (def::class polar (me norm arg)
             (me (* norm (math.cos arg))
                 (* norm (math.sin arg))))

       (def __add__ (self other)
            (Complex (+ self.real other.real)
                     (+ self.imag other.imag)))

       (def __sub__ (self other)
            (Complex (- self.real other.real)
                     (- self.imag other.imag)))

       (def __mul__ (self other)
            (Complex (- (* self.real other.real)
                        (* self.imag other.imag))
                     (+ (* self.real other.imag)
                        (* self.imag other.real))))

       (def __abs__ (self)
            (math.sqrt (+ (^ self.real 2) (^ self.imag 2))))

       (def _reciprocal (self)
            (let ((normsq (^ (abs self) 2)))
              (Complex (/ self.real normsq)
                       (/ (- self.imag) normsq))))

       (def __div__ (self other)
            (* (other._reciprocal) self))
       
       (def __eq__ (self other)
            (< (abs (- self other)) *epsilon*))
       
       (def __ne__ (self other)
            (not (= self other)))
       
       (def __invert__ (self other)
            (Complex self.real (- self.imag)))
       
       (def __str__ (self)
            (+ (str self.real)
               (if (< self.imag 0) " - " " + ")
               (str (abs self.imag))))

       (def __pow__ (self other)
            (Complex.exp (* other (Complex.log self)))))

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

