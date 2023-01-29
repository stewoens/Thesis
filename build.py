"""
Control flow graph builder.
"""
import ast
import astor

test = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/example.py"

stmnt_types = ['Module' , 'If', 'For', 'While', 'Break', 'Continue', 'ExceptHandler', 'With']

class Link(object):
    """
    Link between blocks in a control flow graph.

    Represents a control flow jump between two blocks. Contains an exitcase in
    the form of an expression, representing the case in which the associated
    control jump is made.
    """

    __slots__ = (
        "source",
        "target",
        "exitcase",
        "highlight",
    )

    def __init__(
        self,
        source,
        target,
        exitcase = None, #ast- Compare
    ):
        assert isinstance(target, Block), "Source of a link must be a block"
        assert isinstance(target, Block), "Target of a link must be a block"
        # Block from which the control flow jump was made.
        self.source = source
        # Target block of the control flow jump.
        self.target = target
        # 'Case' leading to a control flow jump through this link.
        self.exitcase = exitcase

    def __str__(self):
        return "link from {0} to {1}".format(self.source,self.target)

    def __repr__(self):
        # This isn't how repr is supposed to be used... We should be able to
        # deep copy this object by calling eval(repr(link))`.
        if self.exitcase is not None:
            return "{self}, with exitcase {ast.dump(self.exitcase)}"
        return str(self)

    def jumpfrom(self):
        """Return the line of source end"""
        return self.source.end()

    def jumpto(self):
        """Return the line of target start"""
        return self.target.at()

    def get_exitcase(self): #??? what is an exitcase?
        """
        Get a string containing the Python source code corresponding to the
        exitcase of the Link.

        Returns:
            A string containing the source code.
        """
        if self.exitcase:
            return astor.to_source(self.exitcase)
        return ""

def read_file_to_string(filename):
    f = open(filename, 'rt')
    s = f.read()
    f.close()
    return s


class CFGBlock():
    """
    CFG Block.

    A CFG Block contains content, children and parents (and type?).
    """
    def __init__(self, id,typ):
        dict = {"id":id, "type":typ,"content":[],"children":[],"parents":[]}
        self.d= dict
        
    def __init__(self, id,type):
        # Id of the block.
        self.id = id
        # Statements in the block.
        self.content = []
        # type of the block
        self.type =type
        # Calls to functions inside the block (represents context switches to
        # some functions' CFGs).???
        self.func_calls = []
        # Links to predecessors in a control flow graph.
        self.predecessors= []
        # Links to the next blocks in a control flow graph. 
        self.exits = []
        # Function blocks within this block ???
        self.func_blocks = []
        
    def at(self):
        """
        Get the line number of the first statement of the block in the program.
        """
        if self.content and self.content[0].lineno >= 0:
            return self.content[0].lineno
        return -1

    def end(self):
        """
        Get the line number of the last statement of the block in the program.
        """
        if self.content and self.content[-1].lineno >= 0:
            return self.content[-1].lineno
        return -1     

    def is_empty(self):
        """
        Check if the block is empty.

        Returns:
            A boolean indicating if the block is empty (True) or not (False).
        """
        return not self.content

    def add_content(self, node):
        """
        Ive made node be dump(node)so far but maybe can be node as well?
        """
        self.content.append(node)
    
    #not sure how the exits work yet
    def add_exit(self, next, exitcase=None):
        link = Link(self, next, exitcase)
        self.exits.append(link)
        next.predecessors.append(link)



class CFGBuilder():
    """
    Control flow graph builder.

    A control flow graph builder is an ast.NodeVisitor that can walk through
    a program's AST and iteratively build the corresponding CFG.
    """

    def __init__(self):
        self.blocks =[]
        self.lineno = 0
        self.end_lineno = 0


    def new_block(self, typ, content=None):
            """
            Create a new block with a new id.

            Returns:
                A Block object with a new unique id.
            """
            self.current_id += 1
            block = CFGBlock(id =self.current_id, typ =typ)
            if content is not None:
                self.add_statement(block, content)

            self.cfg.append(block)
            
            return block
     
    
    def add_child(self, block, child):
        if child not in block.d["children"]:
            block.d["children"].append(child)
        

    def build(self, tree, entry_id = 0):
        """
        Build a CFG from an AST.

        Args:
            tree: The root of the AST from which the CFG must be built.
            entry_id: Value for the id of the entry block of the CFG.

        Returns:
            The CFG produced from the AST.
        """
        self.cfg = []
        self.current_id = entry_id
        #block =self.new_block(tree.__class__.__name__)
        
        
        self.traverse(tree)
        return self.cfg
        
        
    def traverse(self, node):
        """
        Walk along the AST to generate CFG

        Args:
            tree (AST): the tree to be walked
        return id of Block
        """
        
        # will a new block be generated after a specific content or before 
        #boolean wether can join old node or not (options are 1: add as content 
        #                                                  or 2: add to children (pos))
        pos = len(self.cfg)
        type= node.__class__.__name__
        
        # decide if the current node is Control Flow Relevant or not.
            
        if isinstance(node, ast.Module):
            current_block = self.new_block(type)
            pos+=1 
            for child in ast.iter_child_nodes(node):
                self.add_child(current_block, self.traverse(child))
            
        elif isinstance(node, ast.For):
            current_block = self.new_block(type)
            pos+=1 
            #dump target info
            self.add_statement(current_block,ast.dump(node.target))
            #dump iter info
            self.add_statement(self.cfg[-1],ast.dump(node.iter))
            print node.body
            for child in node.body:
                self.add_child(current_block, self.traverse(child))
                
        elif isinstance(node, ast.If):
            if self.current_block.content:
                # Add the If statement at the beginning of the new block.
                cond_block = self.new_block()
                self.add_statement(cond_block, node)
                self.add_exit(self.current_block, cond_block)
                self.current_block = cond_block
            else:
                # Add the If statement at the end of the current block.
                self.add_statement(self.current_block, node)
            if any(isinstance(node.test, T) for T in (ast.Compare, ast.Call)):
                self.visit(node.test)
            # Create a new block for the body of the if. (storing the True case)
            if_block = self.new_block()

            self.add_exit(self.current_block, if_block, node.test)

            # Create a block for the code after the if-else.
            afterif_block = self.new_block()

            # New block for the body of the else if there is an else clause.
            if node.orelse:
                else_block = self.new_block()
                self.add_exit(self.current_block, else_block, invert(node.test))
                self.current_block = else_block
                # Visit the children in the body of the else to populate the block.
                for child in node.orelse:
                    self.visit(child)
                self.add_exit(self.current_block, afterif_block)
            else:
                self.add_exit(self.current_block, afterif_block, invert(node.test))

            # Visit children to populate the if block.
            self.current_block = if_block
            for child in node.body:
                self.visit(child)
            self.add_exit(self.current_block, afterif_block)

            # Continue building the CFG in the after-if block.
            self.current_block = afterif_block

            # current_block = self.new_block(type)
            # pos+=1 
            # #dump test info
            # self.add_statement(current_block,ast.dump(node.test))
            
            # # have to create seperate children for each because otherwise true & false in same block
            # for child in node.body:
            #     self.add_child(current_block, self.traverse(child))
                
            # else_type= node.orelse[0].__class__.__name__
            # self.new_block(else_type)
            # pos+=1 
        
            # for child in node.orelse:
            #     self.add_child(current_block, self.traverse(child))
            
        # ----------------GENERAL CASE--------------------#
        else:    
            #if the parent is a cfg node, a new node is created
            if self.cfg[-1].d["type"] in stmnt_types:
                current_block =self.new_block(type)
                pos += 1
            else:current_block = self.cfg[-1]
                
            self.add_statement(self.cfg[-1], ast.dump(node))
            #general child traversing
            # for child in ast.iter_child_nodes(node):
            #     self.add_child(current_block, self.traverse(child))
            
        
            
        return pos
            
            
        
   
   
def main():
    tree = ast.parse(read_file_to_string(test), test)
    cfgb = CFGBuilder()
    cfg = cfgb.build(tree)
    # for block in cfg:
    #     print block.d

main()
