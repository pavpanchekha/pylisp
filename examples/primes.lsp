(use timer)

(print 'Python (set! '*python-time*
       (time {{{
primes = [2, 3]
for i in range(primes[-1], 1000, 2):
    if all([i % p for p in primes]):
        primes.append(i)}}})))

(print 'Pylisp (set! '*pylisp-time*
       (time 
         (set! '*primes* '(2 3))
         (for (i (range (last *primes*) 1000 2))
           (if (all (for (p *primes*) (mod i p)))
             (*primes*.append i))))))

(print 'Compiled (set! '*compiled-time*
       (time
         (compile
           '(set! '*primes* '(2 3))
           '(for (i (range (last *primes*) 1000 2))
             (set! 'append? #t)
             (for (p *primes*)
               (if (not (mod i p))
                 (set! 'append? #f)))
             (if append?
               (*primes*.append i)))))))

(print)
(print "Normalized times (Python is 1.0):")
(print "Regular" "\t" (/ *pylisp-time* *python-time*))
(print "Compiled" "\t" (/ *compiled-time* *python-time*))
