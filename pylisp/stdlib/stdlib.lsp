
(def map (f l)
  (if (not l)
     nil
     (cons
       (f (car l))
       (map f (cdr l)))))

(def filter (f l)
  (if (not l)
     nil
     (if (f (car l))
         (cons
           (car l)
           (filter f (cdr l)))
         (filter f (cdr l)))))

(def groups (l n)
     (if (<= (len l) n)
         (list l)
         (cons ([] l (slice 0 n))
               (groups ([] l (slice n #0))))))

(def any (l)
    (> (len (filter I l)) 0))

(def all (l)
    (= (len (filter not l)) 0))

(def zip (l)
    (if (all l)
        (cons
            (map car l)
            (zip (map cdr l)))
        nil))

(def::macro and (x y)
  `(if ,x ,y ,x))

(def::macro or (x y)
  `(if ,x ,x ,y))

(def or (x y)
  (if x y x))

(def and (x y)
  (if x x y))

(def xor (x y)
     (or (and x (not y)) (and y (not x))))

(def cadr (x) (car (cdr x)))
(def cddr (x) (cdr (cdr x)))

(def::macro let (vars . body)
    `((fn ,(map car vars) ,@body) ,@(map cadr vars)))

(def::macro ++ (var)
    `(set! ',var (+ ,var 1)))

(def::macro post++ (var)
    `(- (++ ,var) 1))

(def::macro assert (expr)
    `(if (not ,expr)
        (signal '(error assertion) ',expr)))

(def::macro import (. args)
    (def quoted (x)
        `',x)

    `(set! ',(last args) (#import ,@(map quoted args))))

(def::macro import::macro (. args)
    (def quoted (x)
        `',x)

    `(#import::macro ,@(map quoted args)))

(def::macro use (. args)
    `(block (import ,@args) (import::macro ,@args)))

(def::macro map::macro (f l)
    `(block ,@(map (fn (x) (list f x)) l)))

(def::macro use::all(l)
    `(block ,@(for (i l)
         (+ (list 'use) (if (atom? i) i (list i))))))

(def::macro while (test . body)
    (let ((v1 (gensym)))
      `(let ((,v1 (fn ()
        (if ,test
          (block
            ,@body
            (,v1))))))
        (,v1))))

(def::macro do-while (test . body)
    (let ((v1 (gensym)))
      `(let ((,v1 (fn ()
        ,@body
        (if ,test
            ,v1))))
        (,v1))))

(def::macro for (vardef . body)
    `(map (fn (,(car vardef)) ,@body)
        ,(cadr vardef)))

