
; Set up cxxxxxr functions
(map eval ((fn ()
  (set! 'cadr  {x: (car (cdr x))})
  
  (set! ***exp (fn (l)
                 (+ (map {x: `(,(+ "a" (car x)) (car ,(cadr x)))} l)
                    (map {x: `(,(+ "d" (car x)) (cdr ,(cadr x)))} l)
                    l)))
  (set! ***rec (fn (n)
    (if (not n)
      `((,"" x))
      (***exp (***rec (- n 1))))))

  (map {x: `(set! ,(+ "c" (car x) "r") (fn (x) ,(cadr x)))} 
       (filter {x: (!= (len (car x)) 1)} (***rec 4))))))

(#import::macro 'importtypes) ;This gives us (include)
(include fntypes) ; Ok, now we've bootstrapped our way to a useable lisp!

(include blocktypes)
(include asserttypes)
(include classtypes)

(def::macro ++ (var)
    `(set! ',var (+ ,var 1)))

(def::macro post++ (var)
    `(- (++ ,var) 1))

(def::macro -- (var)
    `(set! ',var (- ,var 1)))

(def::macro post-- (var)
    `(+ (-- ,var) 1))

(def::macro control (name . args)
    `'(,name ,@args))

(def::macro compiled (. body)
    `((compile ,@(map {x:`',x} body))))

(def::macro and (x y)
    (let (g1 (gensym))
      `(let (,g1 ,x)
         (if ,g1 ,y ,g1))))

(def::macro or (x y)
    (let (g1 (gensym))
      `(let (,g1 ,x)
         (if ,g1 ,g1 ,y))))

(def or (x y) (if x y x))
(def and (x y) (if x x y))
(def xor (x y) (!= (bool x) (bool y)))
; Note the use of macros with function backups

