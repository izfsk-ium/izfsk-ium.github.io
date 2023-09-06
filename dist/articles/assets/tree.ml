type 'a tree =
  | Leaf 
  | Node of 'a * 'a tree * 'a tree;;

let my_tree = Node(4,
  Node(2,
    Node(1,Leaf,Leaf),
    Node(3,Leaf,Leaf)
  ),
  Node(5,
    Node(6,Leaf,Leaf),
    Node(9,Leaf,Leaf)
  )
);;

let count_leaves t = 
  let rec acc result = function
    | Leaf -> 0
    | Node(_, Leaf, Leaf) -> 1
    | Node(_, l, r) -> acc