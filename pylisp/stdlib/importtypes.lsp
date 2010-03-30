
(def::macro import (. args)
    `(set! ',(last args) (#import ,@(map {x: `',x} args))))

(def::macro include (. args)
    `(block
       (#import::macro ,@(map {x: `',x} args))
       (#include ,@(map {x: `',x} args))))

(def::macro import::macro (. args)
    `(#import::macro ,@(map {x: `',x} args)))

(def::macro use (. args)
    `(block (import::macro ,@args) (import ,@args)))

(def::macro use::all(. l)
    `(block ,@(for (i l)
         (+ '(use) (if (atom? i) `(,i) i)))))

