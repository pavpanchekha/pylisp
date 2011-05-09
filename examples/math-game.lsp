(use random)
(use timer)

(while #t
    (set! 'value `(+ ,(random.randint 100 200)
                     ,(random.randint 100 200)))
    (if (> (time
            (if (not (= (car (read (+ (str value) " = ")))
                        (eval value)))
              (print "FAILURE")))
           5) ; Five seconds should be more than enough
      (print "Too SLOW!")))

