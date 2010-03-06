
(def::macro import (. args)
    (def quoted (x)
        `',x)

    `(set! ',(last args) (#import ,@(map quoted args))))

(def::macro include (. args)
    (def quoted (x)
        `',x)
    
    `(block
       (#include ,@(map quoted args))
       (#import::macro ,@(map quoted args))))

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

