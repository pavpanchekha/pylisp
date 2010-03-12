(set!::macro 'def::macro (fn (name args . body)
    `(set!::macro ',name (fn ,args ,@body))))

(#import::macro 'fntypes)
(#import::macro 'importtypes)
; Ok, now we've bootstrapped our way to a useable lisp!

(import::macro blocktypes)

(def::macro and (x y)
  `(if ,x ,y ,x))

(def::macro or (x y)
  `(if ,x ,x ,y))

(def or (x y) (if x y x))
(def and (x y) (if x x y))
(def xor (x y) (!= (bool x) (bool y)))

(def cadr (x) (car (cdr x)))
(def cddr (x) (cdr (cdr x)))

(def::macro ++ (var)
    `(set! ',var (+ ,var 1)))

(def::macro post++ (var)
    `(- (++ ,var) 1))

(def::macro assert (expr)
    `(if (not ,expr)
        (signal '(error assertion) ',expr)))

(def::macro control (name . args)
    `'(,name ,@args))
