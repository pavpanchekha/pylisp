(use timer)

(set! '*true-primes* '(2 3 5 7 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71
                       73 79 83 89 97 101 103 107 109 113 127 131 137 139 149
                       151 157 163 167 173 179 181 191 193 197 199 211 223 227
                       229 233 239 241 251 257 263 269 271 277 281 283 293 307
                       311 313 317 331 337 347 349 353 359 367 373 379 383 389
                       397 401 409 419 421 431 433 439 443 449 457 461 463 467
                       479 487 491 499 503 509 521 523 541 547 557 563 569 571
                       577 587 593 599 601 607 613 617 619 631 641 643 647 653
                       659 661 673 677 683 691 701 709 719 727 733 739 743 751
                       757 761 769 773 787 797 809 811 821 823 827 829 839 853
                       857 859 863 877 881 883 887 907 911 919 929 937 941 947
                       953 967 971 977 983 991 997))

(print 'Python (set! '*python-time*
       (time {{{
primes = [2, 3]
for i in range(primes[-1], 1000, 2):
    if all([i % p for p in primes]):
        primes.append(i)
}}}
             (assert (= primes *true-primes*)))))

(print 'Pythonic (set! '*pythonic-time*
       (time {{{
primes = [2, 3]
for i in range(primes[-1], 1000, 2):
    flag = True
    for p in primes:
        if i % p == 0:
            flag = False # I'm not using a break, as that would change the algorithm
    if flag:
        primes.append(i)}}}
             (assert (= primes *true-primes*)))))

(print 'Pylisp (set! '*pylisp-time*
       (time 
         (set! '*primes* '(2 3))
         (for (i (range (last *primes*) 1000 2))
           (if (all (for (p *primes*) (mod i p)))
             (*primes*.append i)))
         (assert (= *primes* *true-primes*)))))

(print 'Compiled (set! '*compiled-time*
       (time
         (compiled
           (set! '*primes* '(2 3))
           (for (i (range (last *primes*) 1000 2))
             (set! 'append? #t)
             (for (p *primes*)
               (if (not (mod i p))
                 (set! 'append? #f)))
             (if append?
               (*primes*.append i)))
           (assert (= *primes* *true-primes*))))))


(print)
(print "Normalized times (Python is 1.0):")
(print "Pythonic" "\t" (/ *pythonic-time* *python-time*))
(print "Regular" "\t" (/ *pylisp-time* *python-time*))
(print "Compiled" "\t" (/ *compiled-time* *python-time*))
