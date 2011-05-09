(use xml etree ElementTree)

(def tree->str (tree)
  (def node-add-str (node str)
    (if (len node)
      (if (:: (last node) 'tail)
        (set! (:: (last node) 'tail) (+ (:: (last node) 'tail) str))
        (set! (:: (last node) 'tail) str))
      (if (:: node 'text)
        (set! (:: node 'text) (+ (:: node 'text) str))
        (set! (:: node 'text) str))))

  (def dequote (l)
    (if (= (car l) "'") (cadr l) l))

  (def rec (tag . tree)
    (let (attrs (dict . (map {x:`(,(car (cadr x)) ,(dequote (cadr (cadr x))))} (filter {x: (and (not (atom? x)) (= (car x) "#:"))} tree))))
        (if (atom? tree)
          tree
          (block
            (let (node (ElementTree.Element tag attrs))
              (for (child tree)
                (if (atom? child)
                  (node-add-str node child)
                  (if (= (car child) "'")
                    (node-add-str node (str (cadr child)))
                    (if (not (= (car child) "#:"))
                      (node.append (rec . child))))))
              node)))))
  (ElementTree.tostring (rec . tree)))

(def str->tree (tree)
  (ElementTree.XML tree)) ;TODO

(assert (= (tree->str '(p #:(style "color:red")
                          Hello (br)
                          World))
           "<p style=\"color:red\">Hello<br />World</p>"))

(def \n->br (s)
  ([] (+ . (for (l ((:: s 'split) "\n"))
             `(',l (br)))) (slice 0 (- 1))))
