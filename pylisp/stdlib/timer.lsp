
(def::macro #time (. body)
    (let ((g1 (gensym)))
      `(block
         (use time)
         (let ((,g1 (time.time)))
           ,@body
           (- (time.time) ,g1)))))

(def::macro time (. body)
    `(- (#time ,@body) ,(#time (#time))))

(def::macro time-n (n . body) ;TODO: Is this unsafe?
    `(/ (time
          (for (i (range ,n))
            ,@body)) ,n))

; I'm really just asserting that no error is raised
(assert (time (^ 2 100)))
(assert (time-n 12 (^ 2 1000)))
(set! 'a 10)
(assert (time-n a (^ 2 1000)))

