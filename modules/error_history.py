"""
this file conatains a tree strucuture that will be used to track errors within interpolation. Each Polynomial will have an element of this tree within it. Whenever a number of polynomials is used to interpolate a new one their trees are forged and the tree thus created will be stored in the newly interpolated polynomial
"""

#imports
from anytree import Node, PreOrderIter, RenderTree
import copy


#globals


class Error_history():
    """
    class that implements tree structure for error tracking
    """

    def __init__(self,error):
        """
        task: inits the object and sets the root element of the tree to the given error \n
        parameters:\n
        return value:
        """

        self.error_tree=Node(error)

    def forge_from_parents(self, parent_histories):
        """
        task: forges the error histories of the given parents and thus creates this ones error tree \n
        parameters:\n
        return value:
        """

        self.error_tree.children=[copy.deepcopy(ph.error_tree) for ph in parent_histories]

    def sum_errors(self):
        """
        task: sum all elements of the error_tree \n
        parameters:\n
        return value: float
        """

        sum=0
        for node in PreOrderIter(self.error_tree):
            sum+=node.name

        return sum

    def render_history(self,verbose=True):
        """
        task: render the error tree \n
        parameters:\n
        return value:
        """

        #rendered_tree=""
        for pre, _, node in RenderTree(self.error_tree):
            if verbose:
                print("%s%s" % (pre,node.name))
            current_line="%s%s" % (pre,node.name)
            yield current_line.strip("\n")
           # rendered_tree=rendered_tree.join("%s%s" % (pre,node.name))  creating this string will exceed memory capabilities for larger trees. do it as a generator
        #return rendered_tree

        
if __name__=="__main__":
    hist_child_1=Error_history(10)
    hist_child_2=Error_history(20)
    hist_parent_1=Error_history(100)
    
    print(hist_parent_1.sum_errors())
    hist_parent_1.forge_from_parents([hist_child_1,hist_child_2])
    print(hist_parent_1.sum_errors())
    hist_parent_1.render_history()

    hist_parent_2=Error_history(300)
    print(hist_parent_2.sum_errors())
    hist_parent_2.forge_from_parents([hist_child_1,hist_child_2])
    hist_parent_2.render_history()
    
    print(hist_parent_1.sum_errors())
    hist_parent_1.render_history()




