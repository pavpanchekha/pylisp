(use tester)

(test "Core language"
    (test "Math"
        (assert (= (mod (^ 2010 17) 17) (mod 2010 17)))
        (assert (= (^ 2 (^ 2 (^ 2 2))) 65536)))

    (test "Function definitions"
        (assert (= ((fn (x) (* x x)) 10) 100)))

    (test "let statement"
        (let ((a 1))
            (assert (= a 1)))

        (let ((f (fn (x) (if (<= x 0) 0 (+ (f (- x 1)) 1)))))
            (assert (= (f 7) 7))))

    (test "set! statement"
        (set! 'a 10)
        (assert (= a 10)))

    (test "def & Recursion"
        (def reverse (l) (reverse-aux l '()))
        (def reverse-aux (l acc)
            (if (not l)
                acc
                (reverse-aux (cdr l) ((cons (car l) acc))))
        (assert (= (reverse '(1 2 3)) '(3 2 1))))))

(test "Exceptions"
    (test "(control ignore)"
        (set! 'flag #f)
        ((fn ()
            (handle 'test (fn ()
                (set! 'flag #t)
                (control ignore)))
            (signal 'test)))
        (assert flag))

    (test "(control return)"
        (assert ((fn ()
            (handle 'test (fn ()
                (control return #t)))
            ((fn ()
                 (signal 'test))))))))

(test "Macros"
    (test "Defining Macros"
        (def::macro betrue (a b)
            #t)
        (assert (betrue 1 17)))

    (test "block::macro"
        (block::macro (set! 'flag #t))
        (assert flag)))

(test "Import"
    (test "Python"
        (use math)
        (assert (= (math.sqrt 4) 2))

        (def sqrt-improve (guess num)
             (/ (+ guess (/ num guess)) 2))

        (def sqrt (num)
             (let ((old num) (curr (/ num 2)) (epsilon (^ .1 8)))
                 (while (> (abs (- curr old)) epsilon)
                        (set! 'old curr)
                        (set! 'curr (sqrt-improve curr num)))

                 curr))
        (assert (= (sqrt 17) (math.sqrt 17))))

    (test "Pylisp"
        (use fodder)
        (assert (= (fodder.dist '(0 0) '(3 4)) 5))))

; Cool! We won!
(signal '(warning success))
