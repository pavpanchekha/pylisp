(def::macro time (. body)
    (let ((g1 (gensym)))
      `(block
         (use time)
         (let ((,g1 (time.time)))
           ,@body
           (- (time.time) ,g1)))))

