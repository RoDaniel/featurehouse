// Automatically generated code.  Edit at your own risk!
// Generated by bali2jak v2002.09.03.



public class AsgExpr extends Expression {

    final public static int ARG_LENGTH = 3 ;
    final public static int TOK_LENGTH = 1 /* Kludge! */ ;

    public AssignmentOperator getAssignmentOperator () {
        
        return (AssignmentOperator) arg [1] ;
    }

    public ConditionalExpression getConditionalExpression () {
        
        return (ConditionalExpression) arg [0] ;
    }

    public Expression getExpression () {
        
        return (Expression) arg [2] ;
    }

    public boolean[] printorder () {
        
        return new boolean[] {false, false, false} ;
    }

    public AsgExpr setParms
    (ConditionalExpression arg0, AssignmentOperator arg1, Expression arg2) {
        
        arg = new AstNode [ARG_LENGTH] ;
        tok = new AstTokenInterface [TOK_LENGTH] ;
        
        arg [0] = arg0 ;            /* ConditionalExpression */
        arg [1] = arg1 ;            /* AssignmentOperator */
        arg [2] = arg2 ;            /* Expression */
        
        InitChildren () ;
        return (AsgExpr) this ;
    }

}
