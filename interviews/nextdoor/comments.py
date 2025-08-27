from typing import List, Optional


class Comment:
    """Representation of a comment"""
    def __init__(self, comment_id: int, parent_id: Optional[int]):
        self.id = comment_id
        self.parent_id = parent_id


class CommentNode:
    """A node for representing the tree structure for comments and their replies."""
    def __init__(
            self,
            comment: Comment,
            parent: Optional['CommentNode']):
        self.comment: Comment = comment
        self.parent: Optional['CommentNode'] = parent
        self.children: List['CommentNode'] = []


def flat_to_tree(comments: List[Comment]) -> List[CommentNode]:
    """Convert the comments from a flat list to a tree-like structure. The comments should be
    returned in the same order provided to the function.

    :param comments: list of comments
    :return: the comments as a tree like structure
    """
    # nodes = []
    commentDict = dict()
    for comment in comments:
        node = CommentNode(comment, None)
        # nodes.append(node)
        commentDict[comment.id] = node
    
    # Create parent link
    for comment_id in commentDict.keys():
        if commentDict[comment_id].comment.parent_id:
            commentDict[comment_id].parent = commentDict[commentDict[comment_id].comment.parent_id]
    
    # create children link
    for comment in comments:
        pComment = comment.parent_id
        if pComment:
            commentDict[pComment].children.append(commentDict[comment.id])
    return commentDict.values()


def print_tree_recursive(comment_node : CommentNode, indent: "   "):
    for cNode in comment_node.children:
        print(indent, cNode.comment.id)
        print_tree_recursive(cNode, indent + "   ")
        

def print_tree(comment_nodes: List[CommentNode]):
    for node in comment_nodes:
        # if root
        if not node.parent:
            print(node.comment.id)
            print_tree_recursive(node, "   ")

# The result of this should contain 3 CommentNodes
tree = flat_to_tree([
      Comment(4, 1),
	  Comment(1, None),
	  Comment(2, None),
	  Comment(3, None),
	  Comment(5, 1),
	  Comment(6, 5),
	  Comment(7, 6),
	  Comment(8, 4),
])

# print(tree)
print_tree(tree)



# 1 2 3
# |\
# 4 5
# | |
# 8 6
#   |
#   7

# print_tree(tree)
"""
1
    4
        8
    5
        6
            7
2
3    
"""