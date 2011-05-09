(use random)
(class::simple Node (p key val left right))

(def left-rotate (node)
  (Node node.left.p node.left.key node.left.val
        node.left.left
        (Node node.p node.key node.val node.left.right node.right)))

(def right-rotate (node)
  (Node node.right.p node.right.key node.right.val
        (Node node.p node.key node.val node.left node.right.left)
        node.right.right))

(def get (key root)
  (cond
    ((not root)
     (signal '(error not-found key get) key))
    ((< key root.key)
     (get key root.left))
    ((> key root.key)
     (get key root.right))
    ((= key root.key)
     root.val)))

(def in (key root)
  (cond
    ((not root)
     #f)
    ((< key root.key)
     (in key root.left))
    ((> key root.key)
     (in key root.right))
    ((= key root.key)
     #t)))

(def set (key val root #:(p (random.randint 0 1000000000)))
  (cond
    ((not root)
     (Node p key val #0 #0))
    ((< key root.key)
     (let (new (Node root.p root.key root.val
                     (set key val root.left #:(p p))
                     root.right))
       (if (< new.left.p new.p)
         (left-rotate new)
         new)))
    ((> key root.key)
     (let (new (Node root.p root.key root.val
                     root.left
                     (set key val root.right #:(p p))))
       (if (< new.right.p new.p)
         (right-rotate new)
         new)))
    ((= key root.key)
     (Node root.p root.key val root.left root.right))))

(def split (key root)
  (let (ins (set key #0 root #:(p (- 1))))
    `(,ins.left ,ins.right)))

(def merge (left right)
  (cond
    ((not left)
     right)
    ((not right)
     left)
    ((< left.p right.p)
     (Node left.p  left.key  left.val  (merge left.left left.right) right))
    (#t
     (Node right.p right.key right.val left (merge right.left right.right)))))

(def del (key root)
  (cond
    ((not root)
     (signal '(error not-found key del) key))
    ((< key root.key)
     (Node root.p root.key root.val (del key root.left) root.right))
    ((> key root.key)
     (Node root.p root.key root.val root.left (del key root.right)))
    ((= key root.key)
     (merge root.left root.right))))

(def treap->list (root)
  (if (is root Node)
    `(,root.key ,(treap->list root.left) ,(treap->list root.right))
    root))

(def depth (root)
  (if (not root)
    0
    (max (+ 1 (depth root.left)) (+ 1 (depth root.right)))))

(use tester)
(test "Sanity check"
  (let (treap #0)
    (set! treap (set 5 'a treap))
    (set! treap (set 7 'b treap))
    (assert (= (get 5 treap) 'a))
    (assert (= (get 7 treap) 'b))
    (set! treap (set 2 'c treap))
    (assert (= (get 2 treap) 'c))
    (set! treap (set 2 'd treap))
    (assert (= (get 2 treap) 'd))
    (set! treap (del 5 treap))
    (assert (not (in 5 treap)))))
(test "Fairly Balanced"
  (let (treap #0)
    (signal '(warning test slow-test) "Balancing test")
    (for (i (range 1000))
      (set! treap (set i #0 treap)))
    (assert (< (depth treap) 30))))
