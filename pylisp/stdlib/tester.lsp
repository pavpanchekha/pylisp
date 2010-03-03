(def::macro test (name . body)
    `((fn ()
          (if (has '*test-name*)
              (set! '*test-name* (+ *test-name* "::" ,name))
              (set! '*test-name* ,name))
          (handle '(error assertion) (fn (err)
              (signal '(warning failed-test) *test-name*)
              (control return)))
          ,@body)))

(test "Arithmetic"
      (test "Addition"
            (assert (= (+ 1 3) 4))
            (assert (= (+ 5.5 2.7) 8.2))))
